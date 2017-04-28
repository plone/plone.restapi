# -*- coding: utf-8 -*-
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone import api

import unittest
import transaction


class TestHistoryEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory(
            'Document',
            id='doc_with_history',
            title='My Document'
        )
        self.doc = self.portal.doc_with_history
        self.doc.setTitle('Current version')

        api.content.transition(self.doc, 'publish')

        self.endpoint_url = '{}/@history'.format(self.doc.absolute_url())

        transaction.commit()

    def test_get_types(self):
        # Check if we have all history types in our test setup
        response = self.api_session.get(self.endpoint_url)
        data = response.json()

        types = [item['type'] for item in data]

        self.assertEqual(set(['versioning', 'workflow']), set(types))

    def test_get_datastructure(self):
        response = self.api_session.get(self.endpoint_url)
        data = response.json()

        actor_keys = ['@id', 'id', 'fullname', 'username']

        main_keys = [
            'action',
            'actor',
            'comments',
            'time',
            'transition_title',
            'type',
        ]

        history_keys = main_keys + [
            'content_url',
            'revert_url',
            'version_id'
        ]

        workflow_keys = main_keys + [
            'review_state',
            'state_title',
        ]

        for item in data:
            # Make sure we'll add tests when new history types are added.
            self.assertIn(item['type'], ['versioning', 'workflow'])

            if item['type'] == 'versioning':
                self.assertEqual(set(item.keys()), set(history_keys))
            else:
                self.assertEqual(set(item.keys()), set(workflow_keys))

            self.assertEqual(set(item['actor'].keys()), set(actor_keys))
