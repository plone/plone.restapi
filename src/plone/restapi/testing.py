# -*- coding: utf-8 -*-

# pylint: disable=E1002
# E1002: Use of super on an old style class

from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting
from urlparse import urljoin
from urlparse import urlparse

from plone.testing import z2

from zope.configuration import xmlconfig

import requests


class PlonerestapiLayer(PloneSandboxLayer):

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
        applyProfile(portal, 'Products.Archetypes:Archetypes')
        applyProfile(portal, 'plone.restapi:default')
        applyProfile(portal, 'plone.restapi:testing')

PLONE_RESTAPI_FIXTURE = PlonerestapiLayer()
PLONE_RESTAPI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_FIXTURE,),
    name="PlonerestapiLayer:Integration"
)
PLONE_RESTAPI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PlonerestapiLayer:Functional"
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
