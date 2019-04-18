# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import json
import transaction
import unittest


class TestAddons(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_get_addon_record(self):
        response = self.api_session.get('/@addons/plone.session')

        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)

        self.assertEqual(result['@id'], self.portal_url + u'/plone/@addons/plone.session')
        self.assertEqual(result['id'], u'plone.session')
        # self.assertEqual(result['is_installed'], False)
        self.assertEqual(result['title'], u'Session refresh support')
        self.assertEqual(result['description'], u'Optional plone.session refresh support')
        self.assertEqual(result['profile_type'], u'default')
        self.assertEqual(result['upgrade_info'], {})
        self.assertEqual(result['install_profile_id'], u'plone.session:default')

    def test_get_addon_listing(self):
        response = self.api_session.get('/@addons')

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn('items', response)

    def test_install_addon(self):
        # Check to make sure the addon is currently shown as not installed

        response = self.api_session.post('/@addons/plone.session/install')
        self.assertEqual(response.status_code, 204)
        response = response.json()

        # Check to make sure the addon is currently shown as installed
        self.fail()

    def test_install_addon_with_representation(self):
        # Check to make sure the addon is currently shown as not installed

        response = self.api_session.post(
            '/@addons/plone.session/install',
            headers={'Prefer': 'return=representation'})
        self.assertEqual(response.status_code, 200)
        response = response.json()

        # Check to make sure the addon is currently shown as installed
        self.fail()

    def test_uninstall_addon(self):

        # Check to make sure the addon is currently shown as installed

        response = self.api_session.post('/@addons/plone.session/uninstall')

        self.assertEqual(response.status_code, 204)
        response = response.json()

        # Check to make sure the addon is currently shown as not installed

        self.fail()

    def test_uninstall_addon_with_representation(self):

        # Check to make sure the addon is currently shown as installed

        response = self.api_session.post(
            '/@addons/plone.session/uninstall',
            headers={'Prefer': 'return=representation'})

        self.assertEqual(response.status_code, 200)
        response = response.json()

        # Check to make sure the addon is currently shown as not installed

        self.fail()

    def test_upgrade_addon(self):
        response = self.api_session.post('/@addons/plone.session/upgrade')

        self.assertEqual(response.status_code, 204)

        response = response.json()

        self.fail()

    def test_upgrade_addon_with_representation(self):
        response = self.api_session.post(
            '/@addons/plone.session/upgrade',
            headers={'Prefer': 'return=representation'})

        self.assertEqual(response.status_code, 200)

        response = response.json()

        self.fail()