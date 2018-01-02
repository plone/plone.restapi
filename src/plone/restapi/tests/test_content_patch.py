# -*- coding: utf-8 -*-
from Products.CMFCore.PortalContent import PortalContent
from Products.CMFCore.utils import getToolByName
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import requests
import transaction
import unittest


class TestContentPatch(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory(
            'Document',
            id='doc1',
            title='My Document'
        )
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(self.portal.doc1, 'publish')
        transaction.commit()

    def test_patch_document(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"title": "Patched Document"}',
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        self.assertEqual("Patched Document", self.portal.doc1.Title())

    def test_patch_document_with_representation(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={
                'Accept': 'application/json',
                'Prefer': 'return=representation'
            },
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"title": "Patched Document"}',
        )
        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json()['title'], "Patched Document")
        transaction.begin()
        self.assertEqual("Patched Document", self.portal.doc1.Title())

    def test_patch_document_with_invalid_body_returns_400(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='foo',
        )
        self.assertEqual(400, response.status_code)
        self.assertIn('DeserializationError', response.text)

    def test_patch_undeserializable_object_returns_501(self):
        obj = PortalContent()
        obj.id = 'obj1'
        obj.portal_type = 'Undeserializable Type'
        self.portal._setObject(obj.id, obj)
        transaction.commit()

        response = requests.patch(
            self.portal.obj1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            data='{"id": "patched_obj1"}',
        )
        self.assertEqual(501, response.status_code)
        self.assertIn('Undeserializable Type', response.text)

    def test_patch_document_returns_401_unauthorized(self):
        response = requests.patch(
            self.portal.doc1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            data='{"title": "Patched Document"}',
        )
        self.assertEqual(401, response.status_code)

    def test_patch_image_with_the_contents_of_the_get_preserves_image(self):
        response = requests.post(
            self.portal.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                '@type': 'Image',
                'image': {
                    'data': u'R0lGODlhAQABAIAAAP///wAAACwAAAAAAQABAAACAkQBADs=',  # noqa
                    'encoding': u'base64',
                    'content-type': u'image/gif',
                }
            },
        )
        transaction.commit()

        response = response.json()
        image_url = self.portal[response['id']].absolute_url()
        response = requests.patch(
            image_url,
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json=response
        )
        transaction.commit()
        response = requests.get(
            image_url,
            headers={'Accept': 'application/json'})

        self.assertTrue(response.json()['image'])
        self.assertIn('content-type', response.json()['image'])
        self.assertIn('download', response.json()['image'])
