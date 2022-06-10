# pylint: disable=E1002
# E1002: Use of super on an old style class
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.i18n.locales.interfaces import IContentLanguages
from plone.app.i18n.locales.interfaces import IMetadataLanguages
from plone.app.iterate.testing import PLONEAPPITERATEDEX_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
from plone.restapi.tests.dxtypes import INDEXES as DX_TYPES_INDEXES
from plone.restapi.tests.helpers import add_catalog_indexes
from plone.testing import zope
from plone.testing.layer import Layer
from plone.uuid.interfaces import IUUIDGenerator
from Products.CMFCore.utils import getToolByName
from requests.exceptions import ConnectionError
from urllib.parse import urljoin
from urllib.parse import urlparse
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.interface import implementer

import collective.MockMailHost
import os
import re
import requests
import time


try:
    from plone.app.caching.testing import PloneAppCachingBase
except ImportError:
    # we get an import error in Plone 5.2 and in 6.0a4 an earlier
    PloneAppCachingBase = None

ENABLED_LANGUAGES = ["de", "en", "es", "fr"]


def set_available_languages():
    """Limit available languages to a small set.

    We're doing this to avoid excessive language lists in dumped responses
    for docs. Depends on our own ModifiableLanguages components
    (see plone.restapi:testing profile).
    """
    getUtility(IContentLanguages).setAvailableLanguages(ENABLED_LANGUAGES)
    getUtility(IMetadataLanguages).setAvailableLanguages(ENABLED_LANGUAGES)


def set_supported_languages(portal):
    """Set supported languages to the same predictable set for all test layers."""
    language_tool = getToolByName(portal, "portal_languages")
    for lang in ENABLED_LANGUAGES:
        language_tool.addSupportedLanguage(lang)


def enable_request_language_negotiation(portal):
    """Enable request language negotiation during tests.

    This is so we can use the Accept-Language header to request translated
    pieces of content in different languages.
    """
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ILanguageSchema, prefix="plone")
    settings.use_request_negotiation = True


class DateTimeFixture(Layer):
    def setUp(self):
        tz = "UTC"
        os.environ["TZ"] = tz
        time.tzset()

        # Patch DateTime's timezone for deterministic behavior.
        from DateTime import DateTime

        self.DT_orig_localZone = DateTime.localZone
        DateTime.localZone = lambda cls=None, ltm=None: tz

        from plone.dexterity import content

        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)
        self._orig_content_zone = content._zone
        content._zone = tz

    def tearDown(self):
        if "TZ" in os.environ:
            del os.environ["TZ"]
        time.tzset()

        from DateTime import DateTime

        DateTime.localZone = self.DT_orig_localZone

        from plone.dexterity import content

        content._zone = self._orig_content_zone
        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)


DATE_TIME_FIXTURE = DateTimeFixture()


class PloneRestApiDXLayer(PloneSandboxLayer):

    defaultBases = (DATE_TIME_FIXTURE, PLONE_APP_CONTENTTYPES_FIXTURE)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        xmlconfig.file("configure.zcml", plone.restapi, context=configurationContext)
        xmlconfig.file("testing.zcml", plone.restapi, context=configurationContext)

        self.loadZCML(package=collective.MockMailHost)
        zope.installProduct(app, "plone.restapi")

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])

        set_supported_languages(portal)

        applyProfile(portal, "plone.restapi:default")
        applyProfile(portal, "plone.restapi:testing")
        add_catalog_indexes(portal, DX_TYPES_INDEXES)
        set_available_languages()
        enable_request_language_negotiation(portal)
        quickInstallProduct(portal, "collective.MockMailHost")
        applyProfile(portal, "collective.MockMailHost:default")
        states = portal.portal_workflow["simple_publication_workflow"].states
        states["published"].title = "Published with accent é"  # noqa: E501


PLONE_RESTAPI_DX_FIXTURE = PloneRestApiDXLayer()
PLONE_RESTAPI_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE,),
    name="PloneRestApiDXLayer:Integration",
)
PLONE_RESTAPI_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneRestApiDXLayer:Functional",
)


class PloneRestApiTestWorkflowsLayer(PloneSandboxLayer):

    defaultBases = (PLONE_RESTAPI_DX_FIXTURE,)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.restapi:testing-workflows")


PLONE_RESTAPI_WORKFLOWS_FIXTURE = PloneRestApiTestWorkflowsLayer()
PLONE_RESTAPI_WORKFLOWS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_WORKFLOWS_FIXTURE,),
    name="PloneRestApiTestWorkflowsLayer:Integration",
)


class PloneRestApiDXPAMLayer(PloneSandboxLayer):

    defaultBases = (DATE_TIME_FIXTURE, PLONE_APP_CONTENTTYPES_FIXTURE)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        xmlconfig.file("configure.zcml", plone.restapi, context=configurationContext)
        xmlconfig.file("testing.zcml", plone.restapi, context=configurationContext)

        zope.installProduct(app, "plone.restapi")

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
        )
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ["Manager"])

        set_supported_languages(portal)
        if portal.portal_setup.profileExists("plone.app.multilingual:default"):
            applyProfile(portal, "plone.app.multilingual:default")
        applyProfile(portal, "plone.restapi:default")
        applyProfile(portal, "plone.restapi:testing")
        add_catalog_indexes(portal, DX_TYPES_INDEXES)
        set_available_languages()
        enable_request_language_negotiation(portal)
        states = portal.portal_workflow["simple_publication_workflow"].states
        states["published"].title = "Published with accent é"  # noqa: E501


PLONE_RESTAPI_DX_PAM_FIXTURE = PloneRestApiDXPAMLayer()
PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_DX_PAM_FIXTURE,), name="PloneRestApiDXPAMLayer:Integration"
)
PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_DX_PAM_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneRestApiDXPAMLayer:Functional",
)

if PloneAppCachingBase is not None:
    # condition and fallback can be removed in a Plone 6.0 only scenario
    class PloneRestApiCachingLayer(PloneAppCachingBase):

        defaultBases = [
            PLONE_RESTAPI_DX_PAM_FIXTURE,
        ]

    PLONE_RESTAPI_CACHING_FIXTURE = PloneRestApiCachingLayer()
    PLONE_RESTAPI_CACHING_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_RESTAPI_CACHING_FIXTURE,),
        name="PloneRestApICachingLayer:Integration",
    )
    PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(
            PLONE_RESTAPI_CACHING_FIXTURE,
            zope.WSGI_SERVER_FIXTURE,
        ),
        name="PloneRestApICachingLayer:Functional",
    )
else:
    PLONE_RESTAPI_CACHING_INTEGRATION_TESTING = None
    PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING = None


class PloneRestApiDXIterateLayer(PloneSandboxLayer):

    defaultBases = (PLONEAPPITERATEDEX_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        xmlconfig.file("configure.zcml", plone.restapi, context=configurationContext)
        xmlconfig.file("testing.zcml", plone.restapi, context=configurationContext)

        zope.installProduct(app, "plone.restapi")


PLONE_RESTAPI_ITERATE_FIXTURE = PloneRestApiDXIterateLayer()
PLONE_RESTAPI_ITERATE_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_ITERATE_FIXTURE,),
    name="PloneRestApiDXIterateLayer:Integration",
)
PLONE_RESTAPI_ITERATE_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_ITERATE_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneRestApiDXIterateLayer:Functional",
)


class PloneRestApIBlocksLayer(PloneSandboxLayer):

    defaultBases = (PLONE_RESTAPI_DX_FIXTURE,)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.restapi:blocks")


PLONE_RESTAPI_BLOCKS_FIXTURE = PloneRestApIBlocksLayer()
PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_BLOCKS_FIXTURE,), name="PloneRestApIBlocksLayer:Integration"
)
PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_BLOCKS_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="PloneRestApIBlocksLayer:Functional",
)


class RelativeSession(requests.Session):
    """A session that takes a base URL and makes requests relative to that
    base if their URL is relative (doesn't begin with a HTTP[S] scheme).
    """

    def __init__(self, base_url, test=None):
        """
        Capture the base URL.  Optionally also capture a test case for cleanup.

        Apparently, network sockets created by the `requests` library can remain open
        even after the full body of the response has been read, despite [the
        docs](https://requests.readthedocs.io/en/latest/user/advanced/#body-content-workflow). In
        particular, this results in `ResourceWarning: unclosed <socket.socket ...>` leak
        warnings when running the tests.  If the `test` kwarg is passed, it will be used
        to register future cleanup calls to close this session and thus also the
        sockets. If passed, it must be an object with a `addCleanup(func)` callable
        attribute, such as instances of `unittest.TestCase`.
        """
        super().__init__()

        if not base_url.endswith("/"):
            base_url += "/"
        self.__base_url = base_url

        if hasattr(test, "addCleanup"):
            # Avoid `ResourceWarning: unclosed <socket.socket ...>`
            test.addCleanup(self.close)

    def request(self, method, url, **kwargs):
        if urlparse(url).scheme not in ("http", "https"):
            url = url.lstrip("/")
            url = urljoin(self.__base_url, url)
        try:
            return super().request(method, url, **kwargs)
        except ConnectionError:
            # On Jenkins we often get one ConnectionError in a seemingly
            # random test, mostly in test_documentation.py.
            # The server is still listening: the port is open.  We retry once.
            time.sleep(1)
            return super().request(method, url, **kwargs)


@implementer(IUUIDGenerator)
class StaticUUIDGenerator:
    """UUID generator that produces stable UUIDs for use in tests.

    Based on code from ftw.testing
    """

    def __init__(self, prefix):
        self.prefix = prefix[:26]
        self.counter = 0

    def __call__(self):
        self.counter += 1
        postfix = str(self.counter).rjust(32 - len(self.prefix), "0")
        return self.prefix + postfix


def register_static_uuid_utility(prefix):
    prefix = re.sub(r"[^a-zA-Z0-9\-_]", "", prefix)
    generator = StaticUUIDGenerator(prefix)
    getGlobalSiteManager().registerUtility(component=generator)


def normalize_html(value):
    # Strip all white spaces of every line, then join on one line.
    # But try to avoid getting 'Go to<a href' instead of 'Go to <a href'.
    lines = []
    for line in value.splitlines():
        line = line.strip()
        if (
            line.startswith("<")
            and not line.startswith("</")
            and not line.startswith("<br")
        ):
            line = " " + line
        lines.append(line)
    return "".join(lines).strip()
