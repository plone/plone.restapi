# -*- coding: utf-8 -*-

# pylint: disable=E1002
# E1002: Use of super on an old style class

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import applyProfile
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.restapi.tests.dxtypes import INDEXES as DX_TYPES_INDEXES
from plone.restapi.tests.helpers import add_catalog_indexes
from urlparse import urljoin
from urlparse import urlparse

from plone.testing import z2

from zope.configuration import xmlconfig

import requests


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

        z2.installProduct(app, 'plone.restapi')

    def setUpPloneSite(self, portal):
        portal.acl_users.userFolderAddUser(
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD, ['Manager'], [])
        login(portal, SITE_OWNER_NAME)
        setRoles(portal, TEST_USER_ID, ['Manager'])
        applyProfile(portal, 'plone.restapi:default')
        applyProfile(portal, 'plone.restapi:testing')
        add_catalog_indexes(portal, DX_TYPES_INDEXES)

PLONE_RESTAPI_DX_FIXTURE = PloneRestApiDXLayer()
PLONE_RESTAPI_DX_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE,),
    name="PloneRestApiDXLayer:Integration"
)
PLONE_RESTAPI_DX_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_DX_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApiDXLayer:Functional"
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

PLONE_RESTAPI_AT_FIXTURE = PloneRestApiATLayer()
PLONE_RESTAPI_AT_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_AT_FIXTURE,),
    name="PloneRestApiATLayer:Integration"
)
PLONE_RESTAPI_AT_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_AT_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PloneRestApiATLayer:Functional"
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
