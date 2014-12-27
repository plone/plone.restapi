# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import applyProfile
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2

from zope.configuration import xmlconfig


class PlonerestapiLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        import plone.restapi
        xmlconfig.file(
            'configure.zcml',
            plone.restapi,
            context=configurationContext
        )

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'plone.restapi:default')

PLONE_RESTAPI_FIXTURE = PlonerestapiLayer()
PLONE_RESTAPI_INTEGRATION_TESTING = IntegrationTesting(
    bases=(PLONE_RESTAPI_FIXTURE,),
    name="PlonerestapiLayer:Integration"
)
PLONE_RESTAPI_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(PLONE_RESTAPI_FIXTURE, z2.ZSERVER_FIXTURE),
    name="PlonerestapiLayer:Functional"
)
