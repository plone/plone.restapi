# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestRegistry(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({'Accept': 'application/json'})

        transaction.commit()

    def test_actions_keys(self):
        response = self.api_session.get('/@actions')

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(['object', 'object_buttons', 'user'],
                         sorted(response.keys()))

    def test_actions_siteroot(self):
        response = self.api_session.get('/@actions')

        self.assertEqual(response.status_code, 200)
        response = response.json()
        # object
        self.assertTrue({
            "icon": "",
            "id": "view",
            "title": "View"} in response["object"])
        self.assertTrue({
            "icon": "",
            "id": "folderContents",
            "title": "Contents"} in response["object"])
        # object_buttons
        self.assertEqual(response["object_buttons"], [])
        # user
        self.assertTrue({
            u'icon': u'',
            u'id': u'preferences',
            u'title': u'Preferences'} in response["user"])
        self.assertTrue({
            "icon": "",
            "id": "plone_setup",
            "title": "Site Setup"} in response["user"])
        self.assertTrue({
            "icon": "",
            "id": "logout",
            "title": "Log out"} in response["user"])

    def test_object_actions_content_object(self):
        self.portal.invokeFactory(
            'Document',
            id='doc1',
            title='My Document'
        )
        transaction.commit()
        url = '%s/@actions' % self.portal.doc1.absolute_url()
        response = self.api_session.get(url)
        self.assertEqual(response.status_code, 200)
        response = response.json()

        # object
        self.assertTrue({
            "icon": "",
            "id": "edit",
            "title": "Edit"} in response["object"])
        # object_buttons
        self.assertTrue({
            "icon": "",
            "id": "copy",
            "title": "Copy"} in response["object_buttons"])

    def test_actions_anon(self):
        response = self.anon_api_session.get('/@actions')

        self.assertEqual(response.status_code, 200)
        response = response.json()

        # object
        self.assertTrue({
            "icon": "",
            "id": "view",
            "title": "View"} in response["object"])

        # logged in user actions are not available
        self.assertTrue({
            u'icon': u'',
            u'id': u'preferences',
            u'title': u'Preferences'} not in response["user"])
        self.assertTrue({
            "icon": "",
            "id": "plone_setup",
            "title": "Site Setup"} not in response["user"])
        self.assertTrue({
            "icon": "",
            "id": "logout",
            "title": "Log out"} not in response["user"])

        # But there is a login action
        self.assertTrue({
            "icon": "",
            "id": "login",
            "title": "Log in"} in response["user"])
