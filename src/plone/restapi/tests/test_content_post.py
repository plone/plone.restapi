# -*- coding: utf-8 -*-
from datetime import datetime
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from plone.restapi import HAS_PLONE_APP_EVENT_20

import pytz
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

    def test_post_to_folder_creates_document(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertEqual("My Document", self.portal.folder1.mydocument.Title())
        self.assertEqual("Document", response.json().get('@type'))
        self.assertEqual("mydocument", response.json().get('id'))
        self.assertEqual("My Document", response.json().get('title'))

        expected_url = "http://localhost:55001/plone/folder1/mydocument"
        self.assertEqual(expected_url, response.json().get('@id'))

    def test_post_to_folder_creates_folder(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Folder",
                "id": "myfolder",
                "title": "My Folder",
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertEqual("My Folder", self.portal.folder1.myfolder.Title())
        self.assertEqual("Folder", response.json().get('@type'))
        self.assertEqual("myfolder", response.json().get('id'))
        self.assertEqual("My Folder", response.json().get('title'))

        expected_url = "http://localhost:55001/plone/folder1/myfolder"
        self.assertEqual(expected_url, response.json().get('@id'))

    def test_post_without_type_returns_400(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "id": "mydocument",
                "title": "My Document",
            },
        )
        self.assertEqual(400, response.status_code)
        self.assertIn("Property '@type' is required", response.content)

    def test_post_without_id_creates_id_from_title(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "title": "My Document",
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertIn('my-document', self.portal.folder1)

    def test_post_without_id_creates_id_from_filename(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "File",
                "title": "My File",
                "file": {
                    "filename": "test.txt",
                    "data": "Spam and Eggs",
                    "content_type": "text/plain",
                },
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertIn('test.txt', self.portal.folder1)

    def test_post_with_id_already_in_use_returns_400(self):
        self.portal.folder1.invokeFactory('Document', 'mydocument')
        transaction.commit()
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
            },
        )
        self.assertEqual(400, response.status_code)

    def test_post_to_folder_returns_401_unauthorized(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
            },
        )
        self.assertEqual(401, response.status_code)


class TestFolderCreateAT(unittest.TestCase):

    layer = PLONE_RESTAPI_AT_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)
        self.portal.invokeFactory(
            'Folder',
            id='folder1',
            title='My Folder'
        )
        # wftool = getToolByName(self.portal, 'portal_workflow')
        # wftool.doActionFor(self.portal.folder1, 'publish')
        transaction.commit()

    def test_post_without_id_creates_id_from_title_for_archetypes(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={
                "@type": "ATTestDocument",
                "title": "My Document",
                "testRequiredField": "My Value"
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertIn('my-document', self.portal.folder1)

    def test_id_from_filename(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
            json={
                "@type": "File",
                "file": {"filename": "test.txt", "data": "Foo bar"},
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        self.assertIn('test.txt', self.portal.folder1)


class TestEventCT(unittest.TestCase):

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

    @unittest.skipIf(HAS_PLONE_APP_EVENT_20, 'Valid for p.a.event<2.0 only')
    def test_post_to_folder_creates_event_with_correct_TZ(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Event",
                "id": "myevent2",
                "title": "My Event",
                "start": DateTime(datetime(2018, 1, 1, 10, 0)).ISO8601(),
                "end": DateTime(datetime(2018, 1, 1, 12, 0)).ISO8601(),
                "timezone": 'Asia/Saigon'
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            response.json()['start'], u'2018-01-01T10:00:00+07:00')

        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Event",
                "id": "myevent",
                "title": "My Event",
                "start": DateTime(datetime(2013, 1, 1, 10, 0)).ISO8601(),
                "end": DateTime(datetime(2013, 1, 1, 12, 0)).ISO8601(),
                "timezone": 'Europe/Madrid'
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            response.json()['start'], u'2013-01-01T10:00:00+01:00')

    @unittest.skipIf(HAS_PLONE_APP_EVENT_20, 'Valid for p.a.event<2.0 only')
    def test_post_creates_event_with_correct_TZ_using_UTC_offset(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Event",
                "id": "myevent",
                "title": "My Event",
                "start": datetime(
                    2013, 1, 1, 10, 0, 0, 0, pytz.UTC).isoformat(),
                "end": datetime(
                    2013, 1, 1, 12, 0, 0, 0, pytz.UTC).isoformat(),
                "timezone": 'Europe/Madrid'
            },
        )

        self.assertEqual(201, response.status_code)
        self.assertEqual(
            response.json()['start'], u'2013-01-01T10:00:00+01:00')

    @unittest.skipIf(not HAS_PLONE_APP_EVENT_20, 'Valid for p.a.event<2.0 only')  # noqa
    def test_pavent_20_post_to_folder_creates_event_with_correct_TZ(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Event",
                "id": "myevent2",
                "title": "My Event",
                "start": pytz.timezone('Asia/Saigon').localize(datetime(2018, 1, 1, 10, 0)).isoformat(),  # noqa
                "end": pytz.timezone('Asia/Saigon').localize(datetime(2018, 1, 1, 12, 0)).isoformat(),  # noqa
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            response.json()['start'], u'2018-01-01T03:00:00+00:00')

        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Event",
                "id": "myevent",
                "title": "My Event",
                "start": pytz.timezone('Europe/Berlin').localize(datetime(
                    2013, 1, 1, 10, 0)).isoformat(),
                "end": pytz.timezone('Europe/Berlin').localize(datetime(
                    2013, 1, 1, 12, 0)).isoformat(),
            },
        )
        self.assertEqual(201, response.status_code)
        self.assertEqual(
            response.json()['start'], u'2013-01-01T09:00:00+00:00')
