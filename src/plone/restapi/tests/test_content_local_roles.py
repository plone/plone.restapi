# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.restapi.serializer.local_roles import SerializeLocalRolesToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from zope.component import getGlobalSiteManager

import requests
import transaction
import unittest


class TestFolderCreate(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory(
            'Folder',
            id='folder1',
            title='My Folder'
        )
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(self.portal.folder1, 'publish')

        self.portal.folder1.invokeFactory(
            'Document',
            id='doc1',
            title='My Document'
        )

        transaction.commit()

    def _get_ac_local_roles_block(self, obj):
        return bool(
            getattr(aq_base(self.portal.folder1),
                    '__ac_local_roles_block__',
                    False))

    def test_sharing_search(self):
        '''A request to @sharing should support the search parameter. '''
        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        non_search_entries = response.json()['entries']

        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing?search=admin',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        search_entries = response.json()['entries']

        # Did we find anything?
        self.assertNotEqual(len(non_search_entries), len(search_entries))

    def test_sharing_search_roundtrip(self):
        '''Search for a user and use save roles
        '''
        # Make sure we don't already have admin
        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertNotIn(
            'admin', [x['id'] for x in response.json()['entries']]
        )

        # Now find admin and set roles
        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing?search=admin',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        roles = [x for x in response.json()['entries'] if x['id'] == 'admin']
        roles = roles[0]['roles']

        new_roles = dict([(key, not val) for key, val in roles.items()])
        payload = {'entries': [{'id': 'admin', 'roles': new_roles}]}

        response = requests.post(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json=payload,
        )
        self.assertEqual(204, response.status_code)

        # Now we should have admin in @sharing
        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertIn(
            'admin', [x['id'] for x in response.json()['entries']]
        )

        # with the same roles as set
        roles = [x for x in response.json()['entries'] if x['id'] == 'admin']
        roles = roles[0]['roles']
        self.assertEqual(new_roles, roles)

    def test_sharing_requires_delegate_roles_permission(self):
        '''A response for an object without any roles assigned'''
        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
        )

        self.assertEqual(response.status_code, 403)

    def test_get_local_roles_none_assigned(self):
        '''A response for an object without any roles assigned'''
        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {u'available_roles': [u'Contributor', u'Editor', u'Reviewer', u'Reader'],  # noqa
             u'entries': [{
                 u'disabled': False,
                 u'id': u'AuthenticatedUsers',
                 u'login': None,
                 u'roles': {u'Contributor': False,
                            u'Editor': False,
                            u'Reader': False,
                            u'Reviewer': False},
                 u'title': u'Logged-in users',
                 u'type': u'group'}],
             u'inherit': True}
        )

    def test_get_local_roles_with_user(self):
        api.user.grant_roles(username=TEST_USER_ID,
                             obj=self.portal.folder1,
                             roles=['Reviewer'])
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {u'available_roles': [u'Contributor', u'Editor', u'Reviewer', u'Reader'],  # noqa
             u'entries': [
                {
                    u'disabled': False,
                    u'id': u'AuthenticatedUsers',
                    u'login': None,
                    u'roles': {u'Contributor': False,
                               u'Editor': False,
                               u'Reader': False,
                               u'Reviewer': False},
                    u'title': u'Logged-in users',
                    u'type': u'group'},
                {
                    u'disabled': False,
                    u'id': u'test_user_1_',
                    u'roles': {u'Contributor': False,
                               u'Editor': False,
                               u'Reader': False,
                               u'Reviewer': True},
                    u'title': u'test-user',
                    u'type': u'user'}],
             u'inherit': True}
        )

    def test_set_local_roles_for_user(self):

        pas = getToolByName(self.portal, 'acl_users')
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal.folder1),
            (('admin', ('Owner',), 'user', 'admin'),)
        )

        response = requests.post(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'entries': [{
                    u'id': TEST_USER_ID,
                    u'roles': {u'Contributor': False,
                               u'Editor': False,
                               u'Reader': True,
                               u'Reviewer': True},
                    u'type': u'user'}],
            },
        )

        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal.folder1),
            (('admin', ('Owner',), 'user', 'admin'),
             ('test-user', (u'Reviewer', u'Reader'),
              'user', u'test_user_1_'))
        )

    def test_unset_local_roles_for_user(self):
        api.user.grant_roles(username=TEST_USER_ID,
                             obj=self.portal.folder1,
                             roles=['Reviewer', 'Reader'])
        transaction.commit()

        pas = getToolByName(self.portal, 'acl_users')
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal.folder1),
            (('admin', ('Owner',), 'user', 'admin'),
             ('test-user', ('Reviewer', 'Reader'), 'user', 'test_user_1_'))
        )

        response = requests.post(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'entries': [{
                    u'id': TEST_USER_ID,
                    u'roles': {u'Contributor': False,
                               u'Editor': False,
                               u'Reader': False,
                               u'Reviewer': True},
                    u'type': u'user'}],
            },
        )

        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(
            pas.getLocalRolesForDisplay(self.portal.folder1),
            (('admin', ('Owner',), 'user', 'admin'),
             ('test-user', (u'Reviewer',),
              'user', u'test_user_1_'))
        )

    def test_get_local_roles_inherit_roles(self):
        # __ac_local_roles_block__ specifies to block inheritance:
        # https://docs.plone.org/develop/plone/security/local_roles.html
        self.portal.folder1.__ac_local_roles_block__ = True
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['inherit'], False)

    def test_set_local_roles_inherit(self):
        self.assertEqual(self._get_ac_local_roles_block(self.portal.folder1),
                         False)

        # block local roles
        response = requests.post(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'inherit': False
            },
        )

        transaction.commit()
        self.assertEqual(self._get_ac_local_roles_block(self.portal.folder1),
                         True)
        # unblock local roles
        response = requests.post(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'inherit': True
            },
        )
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(self._get_ac_local_roles_block(self.portal.folder1),
                         False)

    def test_get_available_roles(self):
        api.user.grant_roles(username=TEST_USER_ID,
                             obj=self.portal.folder1,
                             roles=['Reviewer'])
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn('available_roles', response)
        self.assertIn('Reader', response['available_roles'])

    def test_inherited_global(self):
        api.user.grant_roles(username=TEST_USER_ID, roles=['Reviewer'])
        api.user.grant_roles(
            username=TEST_USER_ID, obj=self.portal.folder1, roles=['Editor']
        )
        transaction.commit()

        response = requests.get(
            self.portal.folder1.doc1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        response = response.json()
        # find our entry
        entry = [x for x in response['entries'] if x['id'] == TEST_USER_ID][0]

        self.assertEqual('global', entry['roles']['Reviewer'])
        self.assertEqual('acquired', entry['roles']['Editor'])

    def test_inherited_global_via_search(self):
        api.user.create(email='jos@henken.local', username='jos')
        api.user.grant_roles(username='jos', roles=['Reviewer'])
        api.user.grant_roles(
            username='jos', roles=['Editor'], obj=self.portal.folder1
        )
        transaction.commit()

        response = requests.get(
            self.portal.folder1.doc1.absolute_url() + '/@sharing?search=jos',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        response = response.json()
        # find our entry
        entry = [x for x in response['entries'] if x['id'] == 'jos'][0]

        self.assertEqual('global', entry['roles']['Reviewer'])
        self.assertEqual('acquired', entry['roles']['Editor'])

    def test_no_serializer_available_returns_501(self):
        # This test unregisters the local_roles adapter. The testrunner can
        # not auto-revert this on test tearDown. Therefore if we ever run
        # into test isolation issues. Start to look here first.
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(SerializeLocalRolesToJson, name='local_roles')

        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 501)
        response = response.json()
        self.assertIn('error', response)
        self.assertEquals(
            u'No serializer available.',
            response['error']['message']
        )

        # we need to re-register the adapter here for following tests
        gsm.registerAdapter(SerializeLocalRolesToJson, name='local_roles')
