# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.textfield.value import RichTextValue
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import requests
import transaction
import unittest


class TestContentGet(unittest.TestCase):

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
        self.portal.folder1.invokeFactory(
            'Document',
            id='doc1',
            title='My Document'
        )
        self.portal.folder1.doc1.text = RichTextValue(
            u"Lorem ipsum.",
            'text/plain',
            'text/html'
        )
        self.portal.folder1.invokeFactory(
            'Folder',
            id='folder2',
            title='My Folder 2'
        )
        self.portal.folder1.folder2.invokeFactory(
            'Document',
            id='doc2',
            title='My Document 2'
        )
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(self.portal.folder1, 'publish')
        wftool.doActionFor(self.portal.folder1.doc1, 'publish')
        wftool.doActionFor(self.portal.folder1.folder2, 'publish')
        wftool.doActionFor(self.portal.folder1.folder2.doc2, 'publish')
        transaction.commit()

    def test_get_content_returns_fullobjects(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + '?fullobjects',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.json()['items']))
        self.assertTrue(
            'title' in response.json()['items'][0].keys()
        )
        self.assertTrue(
            'description' in response.json()['items'][0].keys()
        )
        self.assertTrue(
            'text' in response.json()['items'][0].keys()
        )
        self.assertEqual(
            {
                u'data': u'<p>Lorem ipsum.</p>',
                u'content-type': u'text/plain',
                u'encoding': u'utf-8'
            },
            response.json()['items'][0].get('text')
        )

        # make sure the single document response is the same as the items
        response_doc = requests.get(
            self.portal.folder1.doc1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertEqual(
            response.json()['items'][0],
            response_doc.json()
        )

    def test_get_content_include_items(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + '?include_items=false',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('items', response.json())

    def test_get_content_returns_fullobjects_correct_id(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + '?fullobjects',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.json()['items']))
        self.assertEqual(response.json()['items'][1]['@id'],
                         'http://localhost:55001/plone/folder1/folder2')

    def test_get_content_returns_fullobjects_non_recursive(self):
        response = requests.get(
            self.portal.folder1.absolute_url() + '?fullobjects',
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(2, len(response.json()['items']))
        self.assertTrue('items' not in response.json()['items'][1])

    def test_get_content_includes_related_items(self):
        intids = getUtility(IIntIds)
        self.portal.folder1.doc1.relatedItems = [
            RelationValue(
                intids.getId(
                    self.portal.folder1.folder2.doc2
                )
            )

        ]
        transaction.commit()
        response = requests.get(
            self.portal.folder1.doc1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(1, len(response.json()['relatedItems']))
        self.assertEqual(
            [{
                u'@id': u'http://localhost:55001/plone/folder1/folder2/doc2',
                u'@type': u'Document',
                u'description': u'',
                u'review_state': u'published',
                u'title': u'My Document 2'
            }],
            response.json()['relatedItems']
        )
