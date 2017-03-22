# -*- coding: utf-8 -*-

# pylint: disable=E1002
# E1002: Use of super on an old style class

from Products.CMFCore.utils import getToolByName
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
from plone.restapi.tests.dxtypes import INDEXES as DX_TYPES_INDEXES
from plone.restapi.tests.helpers import add_catalog_indexes
from plone.testing import z2
from plone.uuid.interfaces import IUUIDGenerator
from urlparse import urljoin
from urlparse import urlparse
from zope.component import getGlobalSiteManager
from zope.component import getUtility
from zope.configuration import xmlconfig
from zope.interface import implements
import re

import pkg_resources
import requests
import collective.MockMailHost

try:
    pkg_resources.get_distribution('Products.LinguaPlone')
    LP_INSTALLED = True
except pkg_resources.DistributionNotFound:
    LP_INSTALLED = False

try:
    pkg_resources.get_distribution('plone.app.multilingual')
    PAM_INSTALLED = True
except pkg_resources.DistributionNotFound:
    PAM_INSTALLED = False


def set_available_languages():
    """Limit available languages to a small set.

    We're doing this to avoid excessive language lists in dumped responses
    for docs. Depends on our own ModifiableLanguages components
    (see plone.restapi:testing profile).
    """
    enabled_languages = ['de', 'en', 'es', 'fr']
    getUtility(IContentLanguages).setAvailableLanguages(enabled_languages)
    getUtility(IMetadataLanguages).setAvailableLanguages(enabled_languages)


class PloneRestApiDXLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi
        xmlconfig.file(
            'configure.zcml',
            plone.restapi,
            context=configurationContext
        )
        xmlconfig.file(
            'testing.zcml',
            plone.restapi,
            context=configurationContext
        )

        self.loadZCML(package=collective.MockMailHost)
        z2.installProduct(app, 'plone.restapi')

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        applyProfile(portal, 'plone.restapi:default')
        applyProfile(portal, 'plone.restapi:testing')
        add_catalog_indexes(portal, DX_TYPES_INDEXES)
        set_available_languages()
        quickInstallProduct(portal, 'collective.MockMailHost')
        applyProfile(portal, 'collective.MockMailHost:default')

PLONE_RESTAPI_DX_FIXTURE = PloneRestApiDXLayer()
PLONE_RESTAPI_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE,),
    name="PloneRestApiDXLayer:Integration"
)
PLONE_RESTAPI_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApiDXLayer:Functional"
)

if PAM_INSTALLED:

    class PloneRestApiDXPAMLayer(PloneSandboxLayer):
        defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

        def setUpZope(self, app, configurationContext):
            import plone.restapi
            xmlconfig.file(
                'configure.zcml',
                plone.restapi,
                context=configurationContext
            )
            xmlconfig.file(
                'testing.zcml',
                plone.restapi,
                context=configurationContext
            )

            z2.installProduct(app, 'plone.restapi')

        def setUpPloneSite(self, portal):
            portal.acl_users.userFolderAddUser(
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])
            login(portal, SITE_OWNER_NAME)
            language_tool = getToolByName(portal, 'portal_languages')
            language_tool.addSupportedLanguage('en')
            language_tool.addSupportedLanguage('es')
            applyProfile(portal, 'plone.app.multilingual:default')
            applyProfile(portal, 'plone.restapi:default')
            applyProfile(portal, 'plone.restapi:testing')
            add_catalog_indexes(portal, DX_TYPES_INDEXES)
            set_available_languages()

    PLONE_RESTAPI_DX_PAM_FIXTURE = PloneRestApiDXPAMLayer()
    PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_RESTAPI_DX_PAM_FIXTURE,),
        name="PloneRestApiDXPAMLayer:Integration"
    )
    PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(PLONE_RESTAPI_DX_PAM_FIXTURE, z2.ZSERVER_FIXTURE),
        name="PloneRestApiDXPAMLayer:Functional"
    )


class PloneRestApiATLayer(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import Products.ATContentTypes
        self.loadZCML(package=Products.ATContentTypes)
        import plone.app.dexterity
        self.loadZCML(package=plone.app.dexterity)

        import plone.restapi
        xmlconfig.file(
            'configure.zcml',
            plone.restapi,
            context=configurationContext
        )

        z2.installProduct(app, 'Products.Archetypes')
        z2.installProduct(app, 'Products.ATContentTypes')
        z2.installProduct(app, 'plone.app.collection')
        z2.installProduct(app, 'plone.app.blob')
        z2.installProduct(app, 'plone.restapi')

    def setUpPloneSite(self, portal):
        if portal.portal_setup.profileExists(
                'Products.ATContentTypes:default'):
            applyProfile(portal, 'Products.ATContentTypes:default')
        if portal.portal_setup.profileExists(
                'plone.app.collection:default'):
            applyProfile(portal, 'plone.app.collection:default')

        applyProfile(portal, 'plone.app.dexterity:default')
        applyProfile(portal, 'plone.restapi:default')
        applyProfile(portal, 'plone.restapi:testing')
        set_available_languages()
        portal.portal_workflow.setDefaultChain("simple_publication_workflow")


PLONE_RESTAPI_AT_FIXTURE = PloneRestApiATLayer()
PLONE_RESTAPI_AT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_AT_FIXTURE,),
    name="PloneRestApiATLayer:Integration"
)
PLONE_RESTAPI_AT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_AT_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApiATLayer:Functional"
)

if LP_INSTALLED:
    class PloneRestApiATLPLayer(PloneSandboxLayer):

        defaultBases = (PLONE_FIXTURE,)

        def setUpZope(self, app, configurationContext):
            import Products.ATContentTypes
            self.loadZCML(package=Products.ATContentTypes)
            import plone.app.dexterity
            self.loadZCML(package=plone.app.dexterity)
            import Products.LinguaPlone
            self.loadZCML(package=Products.LinguaPlone)

            import plone.restapi
            xmlconfig.file(
                'configure.zcml',
                plone.restapi,
                context=configurationContext
            )

            z2.installProduct(app, 'Products.Archetypes')
            z2.installProduct(app, 'Products.ATContentTypes')
            z2.installProduct(app, 'Products.LinguaPlone')
            z2.installProduct(app, 'plone.app.collection')
            z2.installProduct(app, 'plone.app.blob')
            z2.installProduct(app, 'plone.restapi')

        def setUpPloneSite(self, portal):
            portal.acl_users.userFolderAddUser(
                SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])

            login(portal, SITE_OWNER_NAME)

            if portal.portal_setup.profileExists(
                    'Products.ATContentTypes:default'):
                applyProfile(portal, 'Products.ATContentTypes:default')
            if portal.portal_setup.profileExists(
                    'plone.app.collection:default'):
                applyProfile(portal, 'plone.app.collection:default')

            applyProfile(portal, 'plone.app.dexterity:default')
            applyProfile(portal, 'Products.LinguaPlone:LinguaPlone')
            applyProfile(portal, 'plone.restapi:default')
            applyProfile(portal, 'plone.restapi:testing')
            portal.portal_languages.addSupportedLanguage("en")
            portal.portal_languages.addSupportedLanguage("es")

    PLONE_RESTAPI_AT_LP_FIXTURE = PloneRestApiATLPLayer()
    PLONE_RESTAPI_AT_LP_INTEGRATION_TESTING = IntegrationTesting(
        bases=(PLONE_RESTAPI_AT_LP_FIXTURE,),
        name="PloneRestApiATLPLayer:Integration"
    )
    PLONE_RESTAPI_AT_LP_FUNCTIONAL_TESTING = FunctionalTesting(
        bases=(PLONE_RESTAPI_AT_LP_FIXTURE, z2.ZSERVER_FIXTURE),
        name="PloneRestApiATLPLayer:Functional"
    )


class RelativeSession(requests.Session):
    """A session that takes a base URL and makes requests relative to that
    base if their URL is relative (doesn't begin with a HTTP[S] scheme).
    """

    def __init__(self, base_url):
        super(RelativeSession, self).__init__()
        if not base_url.endswith('/'):
            base_url += '/'
        self.__base_url = base_url

    def request(self, method, url, **kwargs):
        if urlparse(url).scheme not in ('http', 'https'):
            url = url.lstrip('/')
            url = urljoin(self.__base_url, url)
        return super(RelativeSession, self).request(method, url, **kwargs)


class StaticUUIDGenerator(object):
    """UUID generator that produces stable UUIDs for use in tests.

    Based on code from ftw.testing
    """

    implements(IUUIDGenerator)

    def __init__(self, prefix):
        self.prefix = prefix[:26]
        self.counter = 0

    def __call__(self):
        self.counter += 1
        postfix = str(self.counter).rjust(32 - len(self.prefix), '0')
        return self.prefix + postfix


def register_static_uuid_utility(prefix):
    prefix = re.sub(r'[^a-zA-Z0-9\-_]', '', prefix)
    generator = StaticUUIDGenerator(prefix)
    getGlobalSiteManager().registerUtility(component=generator)
