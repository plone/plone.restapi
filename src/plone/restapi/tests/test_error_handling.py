# -*- coding: utf-8 -*-
from plone.restapi.testing import PLONE_RESTAPI_FUNCTIONAL_TESTING
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.testing.z2 import Browser

import unittest2 as unittest

import json
import requests
import transaction


class TestErrorHandling(unittest.TestCase):

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
        transaction.commit()
        self.browser = Browser(self.app)
        self.browser.handleErrors = False
        self.browser.addHeader(
            'Authorization',
            'Basic %s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD,)
        )

    def test_404_not_found(self):
        response = requests.get(
            self.portal_url + '/non-existing-resource',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.headers.get('content-type'),
            'application/json',
            'When sending a GET request with Accept: application/json ' +
            'the server should respond with sending back application/json.'
        )
        self.assertTrue(json.loads(response.content))
        self.assertEqual(
            'NotFound',
            response.json()['type']
        )

    def test_500_internal_server_error(self):
        pass

    def test_401_unauthorized(self):
        pass
