# -*- coding: utf-8 -*-
# pylint: disable=E1002
# E1002: Use of super on an old style class

from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.i18n.locales.interfaces import IContentLanguages
from plone.app.i18n.locales.interfaces import IMetadataLanguages
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import login
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import quickInstallProduct
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry.interfaces import IRegistry
from plone.restapi.tests.dxtypes import INDEXES as DX_TYPES_INDEXES
from plone.restapi.tests.helpers import add_catalog_indexes
from plone.testing import z2
from plone.testing.layer import Layer
from plone.uuid.interfaces import IUUIDGenerator
from Products.CMFCore.utils import getToolByName
from requests.exceptions import ConnectionError
from six.moves.urllib.parse import urljoin
from six.moves.urllib.parse import urlparse
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.interface import implementer

import collective.MockMailHost
import os
import pkg_resources
import re
import requests
import six
import time


PLONE_VERSION = pkg_resources.parse_version(api.env.plone_version())


try:
    pkg_resources.get_distribution("plone.app.multilingual")
    PAM_INSTALLED = True
except pkg_resources.DistributionNotFound:
    PAM_INSTALLED = False

try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE_5 = False  # pragma: no cover
else:
    PLONE_5 = True  # pragma: no cover

try:
    pkg_resources.get_distribution("Products.Archetypes")
except pkg_resources.DistributionNotFound:
    HAS_AT = False
else:
    HAS_AT = True

try:
    pkg_resources.get_distribution("plone.dexterity")
except pkg_resources.DistributionNotFound:
    HAS_DX = False
else:
    HAS_DX = True

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
    if PLONE_5:
        try:
            # Plone 5.2+
            from plone.i18n.interfaces import ILanguageSchema
        except ImportError:  # pragma: no cover
            # Plone 5.0/5.1
            from Products.CMFPlone.interfaces import ILanguageSchema

        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILanguageSchema, prefix="plone")
        settings.use_request_negotiation = True
    else:
        lang_tool = getToolByName(portal, "portal_languages")
        lang_tool.use_request_negotiation = True


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
        z2.installProduct(app, "plone.restapi")

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
        if six.PY2:  # issue 676
            states["published"].title = u"Published with accent é".encode(
                "utf8"
            )  # noqa: E501
        else:
            states["published"].title = u"Published with accent é"  # noqa: E501


PLONE_RESTAPI_DX_FIXTURE = PloneRestApiDXLayer()
PLONE_RESTAPI_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE,), name="PloneRestApiDXLayer:Integration"
)
PLONE_RESTAPI_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApiDXLayer:Functional",
)


class PloneRestApiDXPAMLayer(PloneSandboxLayer):

    defaultBases = (DATE_TIME_FIXTURE, PLONE_APP_CONTENTTYPES_FIXTURE)

    def setUpZope(self, app, configurationContext):
        import plone.restapi

        xmlconfig.file("configure.zcml", plone.restapi, context=configurationContext)
        xmlconfig.file("testing.zcml", plone.restapi, context=configurationContext)

        z2.installProduct(app, "plone.restapi")

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
        if six.PY2:  # issue 676
            states["published"].title = u"Published with accent é".encode(
                "utf8"
            )  # noqa: E501
        else:
            states["published"].title = u"Published with accent é"  # noqa: E501


PLONE_RESTAPI_DX_PAM_FIXTURE = PloneRestApiDXPAMLayer()
PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_DX_PAM_FIXTURE,), name="PloneRestApiDXPAMLayer:Integration"
)
PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_DX_PAM_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApiDXPAMLayer:Functional",
)


if HAS_AT:

    class PloneRestApiATLayer(PloneSandboxLayer):

        defaultBases = (DATE_TIME_FIXTURE, PLONE_FIXTURE)

        def setUpZope(self, app, configurationContext):
            import Products.ATContentTypes

            self.loadZCML(package=Products.ATContentTypes)
            import plone.app.dexterity

            self.loadZCML(package=plone.app.dexterity)

            import plone.restapi

            xmlconfig.file(
                "configure.zcml", plone.restapi, context=configurationContext
            )

            z2.installProduct(app, "Products.Archetypes")
            z2.installProduct(app, "Products.ATContentTypes")
            z2.installProduct(app, "plone.app.collection")
            z2.installProduct(app, "plone.app.blob")
            z2.installProduct(app, "plone.restapi")

        def setUpPloneSite(self, portal):
            portal.acl_users.userFolderAddUser(
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ["Manager"], []
            )
            set_supported_languages(portal)

            if portal.portal_setup.profileExists("Products.ATContentTypes:default"):
                applyProfile(portal, "Products.ATContentTypes:default")
            if portal.portal_setup.profileExists("plone.app.collection:default"):
                applyProfile(portal, "plone.app.collection:default")

            applyProfile(portal, "plone.app.dexterity:default")
            applyProfile(portal, "plone.restapi:default")
            applyProfile(portal, "plone.restapi:testing")
            set_available_languages()
            enable_request_language_negotiation(portal)
            portal.portal_workflow.setDefaultChain(
                "simple_publication_workflow"
            )  # noqa: E501
            states = portal.portal_workflow[
                "simple_publication_workflow"
            ].states  # noqa: E501
            if six.PY2:  # issue 676
                states["published"].title = u"Published with accent é".encode(
                    "utf8"
                )  # noqa: E501
            else:
                states["published"].title = u"Published with accent é"  # noqa: E501

    PLONE_RESTAPI_AT_FIXTURE = PloneRestApiATLayer()
    PLONE_RESTAPI_AT_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_RESTAPI_AT_FIXTURE,), name="PloneRestApiATLayer:Integration"
    )
    PLONE_RESTAPI_AT_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(PLONE_RESTAPI_AT_FIXTURE, z2.ZSERVER_FIXTURE),
        name="PloneRestApiATLayer:Functional",
    )
else:
    PLONE_RESTAPI_AT_INTEGRATION_TESTING = PLONE_FIXTURE
    PLONE_RESTAPI_AT_FUNCTIONAL_TESTING = PLONE_FIXTURE


class PloneRestApIBlocksLayer(PloneSandboxLayer):

    defaultBases = (PLONE_RESTAPI_DX_FIXTURE,)

    def setUpPloneSite(self, portal):
        applyProfile(portal, "plone.restapi:blocks")


PLONE_RESTAPI_BLOCKS_FIXTURE = PloneRestApIBlocksLayer()
PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_BLOCKS_FIXTURE,), name="PloneRestApIBlocksLayer:Integration"
)
PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_BLOCKS_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApIBlocksLayer:Functional",
)


class RelativeSession(requests.Session):
    """A session that takes a base URL and makes requests relative to that
    base if their URL is relative (doesn't begin with a HTTP[S] scheme).
    """

    def __init__(self, base_url):
        super(RelativeSession, self).__init__()
        if not base_url.endswith("/"):
            base_url += "/"
        self.__base_url = base_url

    def request(self, method, url, **kwargs):
        if urlparse(url).scheme not in ("http", "https"):
            url = url.lstrip("/")
            url = urljoin(self.__base_url, url)
        try:
            return super(RelativeSession, self).request(method, url, **kwargs)
        except ConnectionError:
            # On Jenkins we often get one ConnectionError in a seemingly
            # random test, mostly in test_documentation.py.
            # The server is still listening: the port is open.  We retry once.
            time.sleep(1)
            return super(RelativeSession, self).request(method, url, **kwargs)


@implementer(IUUIDGenerator)
class StaticUUIDGenerator(object):
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
