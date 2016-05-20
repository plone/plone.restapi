# -*- coding: utf-8 -*-
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD

import unittest


class TestServicesTypes(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_get_types(self):
        response = self.api_session.get(
            '{}/@types'.format(self.portal.absolute_url())
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Content-Type'),
            'application/json',
            'Sending a GET request to @types endpoint should respond with ' +
            'Content-Type: "application/json", not ' +
            '"{}"'.format(response.headers.get('Content-Type'))
        )
        self.assertTrue(
            {
                u'@id': u'http://localhost:55001/plone/@types/Collection',
                u'title': u'Collection'
            } in response.json()
        )
        self.assertTrue(
            {
                u'@id': u'http://localhost:55001/plone/@types/Discussion Item',
                u'title': u'Discussion Item'
            } in response.json()
        )
        self.assertTrue(
            {
                u'@id': u'http://localhost:55001/plone/@types/Event',
                u'title': u'Event'
            } in response.json()
        )
        self.assertTrue(
            {
                u'@id': u'http://localhost:55001/plone/@types/File',
                u'title': u'File'
            } in response.json()
        )
        self.assertTrue(
            {
                u'@id': u'http://localhost:55001/plone/@types/Folder',
                u'title': u'Folder'
            } in response.json()
        )
        self.assertTrue(
            {
                u'@id': u'http://localhost:55001/plone/@types/Image',
                u'title': u'Image'
            } in response.json()
        )

    def test_get_types_document(self):
        response = self.api_session.get(
            '{}/@types/Document'.format(self.portal.absolute_url())
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('Content-Type'),
            'application/json+schema',
            'Sending a GET request to @types endpoint should respond with ' +
            'Content-Type: "application/json+schema", not ' +
            '"{}"'.format(response.headers.get('Content-Type'))
        )

    def test_get_types_with_unknown_type(self):
        response = self.api_session.get(
            '{}/@types/UnknownType'.format(self.portal.absolute_url())
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            'application/json',
            response.headers.get('Content-Type'),
            'Sending a GET request to @types endpoint should respond with ' +
            'Content-Type: "application/json", not ' +
            '"{}"'.format(response.headers.get('Content-Type'))
        )

    def test_types_endpoint_only_accessible_for_authenticated_users(self):
        self.api_session.auth = ()
        response = self.api_session.get(
            '{}/@types'.format(self.portal.absolute_url())
        )
        self.assertEqual(response.status_code, 401)
