# -*- coding: utf-8 -*-
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import unittest


class TestRolesGet(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def test_roles_endpoint_lists_roles(self):
        response = self.api_session.get('/@roles')

        self.assertItemsEqual([
            {u'@id': u'http://localhost:55001/plone/@roles/Contributor',
             u'@type': u'role',
             u'id': u'Contributor',
             u'title': u'Contributor'},
            {u'@id': u'http://localhost:55001/plone/@roles/Editor',
             u'@type': u'role',
             u'id': u'Editor',
             u'title': u'Editor'},
            {u'@id': u'http://localhost:55001/plone/@roles/Member',
             u'@type': u'role',
             u'id': u'Member',
             u'title': u'Member'},
            {u'@id': u'http://localhost:55001/plone/@roles/Reader',
             u'@type': u'role',
             u'id': u'Reader',
             u'title': u'Reader'},
            {u'@id': u'http://localhost:55001/plone/@roles/Reviewer',
             u'@type': u'role',
             u'id': u'Reviewer',
             u'title': u'Reviewer'},
            {u'@id': u'http://localhost:55001/plone/@roles/Site Administrator',
             u'@type': u'role',
             u'id': u'Site Administrator',
             u'title': u'Site Administrator'},
            {u'@id': u'http://localhost:55001/plone/@roles/Manager',
             u'@type': u'role',
             u'id': u'Manager',
             u'title': u'Manager'}],
            response.json())

    def test_roles_endpoint_translates_role_titles(self):
        self.api_session.headers.update({'Accept-Language': 'de'})
        response = self.api_session.get('/@roles')

        self.assertItemsEqual([
            u'Hinzuf\xfcgen',
            u'Bearbeiten',
            u'Benutzer',
            u'Ansehen',
            u'Ver\xf6ffentlichen',
            u'Website-Administrator',
            u'Verwalten'],
            [item['title'] for item in response.json()])
