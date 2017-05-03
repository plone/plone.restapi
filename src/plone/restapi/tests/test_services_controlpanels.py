# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


class TestControlpanelsEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_get_listing(self):
        # Do we get a list with at least one item?
        response = self.api_session.get('/@controlpanels')
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertIs(type(data), list)
        self.assertGreater(len(data), 0)

    def test_get_item_nonexisting(self):
        response = self.api_session.get('/@controlpanels/no-way-jose')
        self.assertEqual(404, response.status_code)

    def test_get_item(self):
        response = self.api_session.get('/@controlpanels/editing')
        self.assertEqual(200, response.status_code)
