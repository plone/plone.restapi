# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

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
        transaction.commit()

    def _get_ac_local_roles_block(self, obj):
        return bool(
            getattr(aq_base(self.portal.folder1),
                    '__ac_local_roles_block__',
                    False))

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
             u'inherit': False}
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
             u'inherit': False}
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
        self.portal.folder1.__ac_local_roles_block__ = True
        transaction.commit()

        response = requests.get(
            self.portal.folder1.absolute_url() + '/@sharing',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['inherit'], True)

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
