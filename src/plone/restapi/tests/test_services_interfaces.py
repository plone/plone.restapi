# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.interface import providedBy

import unittest
import transaction


class IDummyInterface(Interface):
    pass


class INotImplementedByAnyoneDummyInterface(Interface):
    pass


class TestInterfaces(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, SITE_OWNER_NAME)

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory(
            'Folder',
            id='folder',
            title='My Folder'
        )
        self.folder = self.portal['folder']
        alsoProvides(self.folder, IDummyInterface)
        transaction.commit()

    def test_folder_interface_in_interfaces(self):
        response = self.api_session.get('/folder/@interfaces')

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            'plone.app.contenttypes.interfaces.IFolder',
            response.json().get('items')
        )

    def test_provided_dummy_interface_in_interfaces(self):
        self.assertTrue(IDummyInterface in providedBy(self.folder))
        response = self.api_session.get('/folder/@interfaces')

        self.assertEqual(response.status_code, 200)

        self.assertIn(
            'plone.restapi.tests.test_services_interfaces.IDummyInterface',
            response.json().get('items')
        )

    def test_not_provided_dummy_interface_not_in_interfaces(self):
        self.assertTrue(
            INotImplementedByAnyoneDummyInterface not in providedBy(self.folder))  # noqa

        response = self.api_session.get('/folder/@interfaces')

        self.assertEqual(response.status_code, 200)

        self.assertNotIn(
            'plone.restapi.tests.test_services_interfaces.INotImplementedByAnyoneDummyInterface',  # noqa
            response.json().get('items')
        )
