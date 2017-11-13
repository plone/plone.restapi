# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

from plone.app.discussion.interfaces import IDiscussionSettings

from zope.component import getUtility

import transaction
import unittest


class TestCommentsEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.portal_url = self.portal.absolute_url()

        # Allow discussion
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        settings.edit_comment_enabled = True
        settings.delete_own_comment_enabled = True

        # doc with comments
        self.doc = api.content.create(
            container=self.portal,
            type='Document',
            id='doc_with_comments',
            title='Document with comments',
            allow_discussion=True
        )
        api.content.transition(self.doc, 'publish')

        api.user.create(username='jos', password='jos', email='jos@plone.org')

        # Admin session
        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # User session
        self.user_session = RelativeSession(self.portal_url)
        self.user_session.headers.update({'Accept': 'application/json'})
        self.user_session.auth = ('jos', 'jos')

        transaction.commit()

    def test_list_datastructure(self):
        url = '{}/@comments'.format(self.doc.absolute_url())
        response = self.api_session.get(url)

        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertEqual(
            set(['items_total', 'items', '@id']),
            set(data.keys())
        )

    def test_list_batching(self):
        url = '{}/@comments'.format(self.doc.absolute_url())

        self.api_session.post(url, json={'text': 'comment 1'})
        self.api_session.post(url, json={'text': 'comment 2'})

        response = self.api_session.get(url, params={'b_size': 1})
        self.assertEqual(200, response.status_code)
        data = response.json()
        self.assertIn('batching', data)

    def test_add_comment_to_root(self):
        url = '{}/@comments'.format(self.doc.absolute_url())

        response = self.api_session.get(url)
        self.assertEqual(0, response.json()['items_total'])

        response = self.api_session.post(url, json={'text': 'comment 1'})
        self.assertEqual(204, response.status_code)
        self.assertIn('location', response.headers)

        response = self.api_session.get(url)
        data = response.json()
        self.assertEqual(1, data['items_total'])
        self.assertIsNone(data['items'][0]['in_reply_to'])
        self.assertIsNone(data['items'][0]['@parent'])

    def test_add_comment_to_comment(self):
        url = '{}/@comments'.format(self.doc.absolute_url())

        response = self.api_session.post(url, json={'text': 'comment 1'})
        self.assertEqual(204, response.status_code)

        response = self.api_session.get(url)
        data = response.json()
        parent_id = data['items'][0]['comment_id']

        SUBTEXT = 'sub comment'

        payload = {'text': SUBTEXT, 'in_reply_to': parent_id}
        response = self.api_session.post(url, json=payload)
        self.assertEqual(204, response.status_code)

        response = self.api_session.get(url)
        data = response.json()
        sub = [x for x in data['items'] if x['text']['data'] == SUBTEXT][0]
        self.assertEqual(parent_id, sub['in_reply_to'])

    def test_update(self):
        url = '{}/@comments'.format(self.doc.absolute_url())
        OLD_TEXT = 'comment 1'
        NEW_TEXT = 'new text'

        self.api_session.post(url, json={'text': OLD_TEXT})

        response = self.api_session.get(url)
        data = response.json()
        item_texts = [x['text']['data'] for x in data['items']]
        self.assertNotIn(NEW_TEXT, item_texts)
        self.assertIn(OLD_TEXT, item_texts)
        comment = data['items'][0]

        payload = {'text': NEW_TEXT}
        response = self.api_session.patch(comment['@id'], json=payload)
        self.assertEqual(204, response.status_code)
        self.assertIn('location', response.headers)

        response = self.api_session.get(url)
        data = response.json()
        item_texts = [x['text']['data'] for x in data['items']]
        self.assertIn(NEW_TEXT, item_texts)
        self.assertNotIn(OLD_TEXT, item_texts)

    def test_permissions_delete_comment(self):
        url = '{}/@comments'.format(self.doc.absolute_url())

        response = self.api_session.post(url, json={'text': 'comment'})
        self.assertEqual(204, response.status_code)

        response = self.api_session.get(url)
        comment_url = response.json()['items'][0]['@id']
        self.assertFalse(comment_url.endswith('@comments'))
        self.assertTrue(response.json()['items'][0]['is_deletable'])

        # Other user may not delete this
        response = self.user_session.delete(comment_url)
        self.assertEqual(401, response.status_code)

        response = self.user_session.get(url)
        self.assertFalse(response.json()['items'][0]['is_deletable'])

        # The owner may
        response = self.api_session.delete(comment_url)
        self.assertEqual(204, response.status_code)

    def test_permissions_update_comment(self):
        url = '{}/@comments'.format(self.doc.absolute_url())

        response = self.api_session.post(url, json={'text': 'comment'})
        self.assertEqual(204, response.status_code)

        response = self.api_session.get(url)
        comment_url = response.json()['items'][0]['@id']
        self.assertFalse(comment_url.endswith('@comments'))
        self.assertTrue(response.json()['items'][0]['is_editable'])

        # Other user may not update this
        response = self.user_session.patch(comment_url, json={'text': 'new'})
        self.assertEqual(401, response.status_code)

        response = self.user_session.get(url)
        self.assertFalse(response.json()['items'][0]['is_editable'])

        # The owner may
        response = self.api_session.patch(comment_url, json={'text': 'new'})
        self.assertEqual(204, response.status_code)
