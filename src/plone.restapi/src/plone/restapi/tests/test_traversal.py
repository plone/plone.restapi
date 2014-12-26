# -*- coding: utf-8 -*-
from plone.restapi.testing import\
    PLONE_RESTAPI_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

import unittest2 as unittest

import json
import requests


class TestTraversal(unittest.TestCase):

    layer = PLONE_RESTAPI_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Document', id='document1')
        self.document = self.portal.document1
        self.document_url = self.document.absolute_url()
        self.portal.invokeFactory('Folder', id='folder1')
        self.folder = self.portal.folder1
        self.folder_url = self.folder.absolute_url()
        import transaction
        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_json_view_document_traversal(self):
        self.browser.open(self.document_url + '/@@json')
        self.assertTrue(json.loads(self.browser.contents))
        self.assertEqual(
            json.loads(self.browser.contents).get('@id'),
            self.document_url
        )

    def test_json_view_folder_traversal(self):
        self.browser.open(self.folder_url + '/@@json')
        self.assertTrue(json.loads(self.browser.contents))
        self.assertEqual(
            json.loads(self.browser.contents).get('@id'),
            self.folder_url
        )

    @unittest.skip('not working yet')
    def test_json_view_site_root_traversal(self):
        self.browser.open(self.portal_url + '/@@json')
        self.assertTrue(json.loads(self.browser.contents))
        self.assertEqual(
            json.loads(self.browser.contents).get('@id'),
            self.portal_url
        )

    def test_document_traversal(self):
        response = requests.get(
            self.document_url,
            headers={'content-type': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('content-type'),
            'application/json',
            'When sending a GET request with content-type: application/json ' +
            'the server should respond with sending back application/json.'
        )
        self.assertEqual(
            response.json()['@id'],
            self.document_url
        )

    def test_folder_traversal(self):
        response = requests.get(
            self.folder_url,
            headers={'content-type': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get('content-type'),
            'application/json',
            'When sending a GET request with content-type: application/json ' +
            'the server should respond with sending back application/json.'
        )
        self.assertEqual(
            response.json()['@id'],
            self.folder_url
        )
