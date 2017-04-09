# -*- coding: utf-8 -*-

from StringIO import StringIO

from base64 import b64encode
from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import login
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.services.content.upload import TUSUpload

import os
import transaction
import unittest

UPLOAD_DATA = 'abcdefgh'
UPLOAD_MIMETYPE = 'text/plain'
UPLOAD_FILENAME = 'test.txt'
UPLOAD_LENGHT = len(UPLOAD_DATA)

UPLOAD_PDF_MIMETYPE = 'application/pdf'
UPLOAD_PDF_FILENAME = 'file.pdf'


class TestTUS(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        # setRoles(self.portal, TEST_USER_ID, ['Member'])
        login(self.portal, SITE_OWNER_NAME)
        transaction.commit()

        self.folder = api.content.create(container=self.portal,
                                         type='Folder',
                                         id='testfolder',
                                         title='Testfolder')
        self.upload_url = '{}/@upload'.format(self.folder.absolute_url())
        transaction.commit()

        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def get_tus_uid_from_url(self, url):
        uid = url.rsplit('/', 1)[-1]
        assert len(uid) == 32
        return uid

    def get_tus_upload_instance(self, uid):
        return TUSUpload(uid)

    def test_tus_option_headers(self):
        response = self.api_session.options(self.upload_url)
        headers = response.headers
        self.assertEqual(response.status_code, 204)
        self.assertEqual(headers['Tus-Version'], '1.0.0')
        self.assertEqual(headers['Tus-Extension'], 'creation')
        self.assertEqual(headers['Tus-Resumable'], '1.0.0')

    def test_tus_post_initialization_requires_header_length(self):
        response = self.api_session.post(self.upload_url)
        self.assertEqual(response.json()['error']['type'], 'Bad Request')
        self.assertEqual(response.json()['error']['message'],
                         'Missing or invalid Upload-Length header')
        self.assertEqual(response.status_code, 400)

    def test_tus_post_initialization(self):
        response = self.api_session.post(
            self.upload_url,
            headers={'Upload-Length': str(UPLOAD_LENGHT)}
            )
        self.assertEqual(response.status_code, 201)
        location = response.headers['Location']
        url_base, uid = location.rsplit('/', 1)
        self.assertEqual(url_base, self.upload_url)
        self.assertEqual(len(uid), 32)
        upload = TUSUpload(uid)
        stored_metadata = upload.metadata()
        self.assertEqual(stored_metadata,
                         {u'length': 8})

    def test_tus_patch_initialization_with_metadata(self):
        metadata = 'filename {},content-type {}'.format(
            b64encode(UPLOAD_FILENAME),
            b64encode(UPLOAD_MIMETYPE))
        response = self.api_session.post(
            self.upload_url,
            headers={'Upload-Length': str(UPLOAD_LENGHT),
                     'Upload-Metadata': metadata}
            )
        self.assertEqual(response.status_code, 201)
        uid = self.get_tus_uid_from_url(response.headers['Location'])
        upload = TUSUpload(uid)
        stored_metadata = upload.metadata()
        self.assertEqual(stored_metadata,
                         {u'content-type': u'text/plain',
                          u'filename': u'test.txt',
                          u'length': 8})

    def test_tus_can_upload_pdf_file(self):
        # initialize the upload with POST
        pdf_file_path = os.path.join(os.path.dirname(__file__),
                                     UPLOAD_PDF_FILENAME)
        pdf_file_size = os.path.getsize(pdf_file_path)
        metadata = 'filename {},content-type {}'.format(
            b64encode(UPLOAD_PDF_FILENAME),
            b64encode(UPLOAD_PDF_MIMETYPE))
        response = self.api_session.post(
            self.upload_url,
            headers={'Upload-Length': str(pdf_file_size),
                     'Upload-Metadata': metadata}
            )
        self.assertEqual(response.status_code, 201)
        location = response.headers['Location']

        # upload the data with PATCH
        pdf_file = open(pdf_file_path, 'rb')
        response = self.api_session.patch(
            location,
            headers={'Content-Type': 'application/offset+octet-stream',
                     'Upload-Offset': '0',
                     'Tus-Resumable': '1.0.0'},
            data=pdf_file)
        self.assertEqual(response.status_code, 204)

        transaction.commit()
        self.assertEqual([UPLOAD_PDF_FILENAME], self.folder.contentIds())

    def test_tus_can_upload_text_file(self):
        # initialize the upload with POST
        metadata = 'filename {},content-type {}'.format(
            b64encode(UPLOAD_FILENAME),
            b64encode(UPLOAD_MIMETYPE))
        response = self.api_session.post(
            self.upload_url,
            headers={'Upload-Length': str(UPLOAD_LENGHT),
                     'Upload-Metadata': metadata}
            )
        self.assertEqual(response.status_code, 201)
        location = response.headers['Location']

        # upload the data with PATCH
        response = self.api_session.patch(
            location,
            headers={'Content-Type': 'application/offset+octet-stream',
                     'Upload-Offset': '0',
                     'Tus-Resumable': '1.0.0'},
            data=StringIO(UPLOAD_DATA))
        self.assertEqual(response.status_code, 204)
