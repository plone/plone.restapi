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
from plone.restapi.testing import RelativeSession
from DateTime import DateTime

import datetime
import requests
import transaction
import unittest


class TestContentPatch(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, SITE_OWNER_NAME)

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

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

    def test_patch_feed_event_with_get_contents(self):
        start_date = DateTime(datetime.datetime.today() +
                              datetime.timedelta(days=1)).ISO8601()
        end_date = DateTime(datetime.datetime.today() +
                            datetime.timedelta(days=1, hours=1)).ISO8601()
        response = self.api_session.post(
            '/',
            json={
                "title": "An Event",
                "@type": "Event",
                "start": start_date,
                "end": end_date,
                "timezone": "Europe/Vienna"
            },
        )

        self.assertEqual(201, response.status_code)
        response = response.json()
        event_id = response['id']
        two_days_ahead = DateTime(datetime.datetime.today() +
                                  datetime.timedelta(days=2))
        response = self.api_session.patch(
            '/{}'.format(event_id),
            json={
                "start": response['start'],
                "end": two_days_ahead.ISO8601()
            }
        )

        self.assertEqual(204, response.status_code)

        response = self.api_session.get('/{}'.format(event_id))
        response = response.json()
        self.assertEquals(
            DateTime(response['end']).day(),
            two_days_ahead.day()
        )

        self.assertEquals(
            DateTime(response['end']).hour(),
            two_days_ahead.hour()
        )
