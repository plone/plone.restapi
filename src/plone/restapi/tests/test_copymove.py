# -*- coding: utf-8 -*-
from ZPublisher.pubevents import PubStart
from base64 import b64encode
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zExceptions import BadRequest
from zope.component import queryUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds

import json
import unittest


class TestCopyMove(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.doc1 = self.portal[self.portal.invokeFactory(
            'Document', id='doc1', title='My Document')]
        self.folder1 = self.portal[self.portal.invokeFactory(
            'Folder', id='folder1', title='My Folder')]

    def traverse(self, path='/plone', accept='application/json', method='GET'):
        request = self.layer['request']
        request.environ['PATH_INFO'] = path
        request.environ['PATH_TRANSLATED'] = path
        request.environ['HTTP_ACCEPT'] = accept
        request.environ['REQUEST_METHOD'] = method
        request._auth = 'Basic %s' % b64encode(
            '%s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        notify(PubStart(request))
        return request.traverse(path)

    def test_copy_single_object(self):
        self.request['BODY'] = '{"source": "%s"}' % self.doc1.absolute_url()
        service = self.traverse('/plone/@copy', method='POST')
        service()
        self.assertIn('copy_of_doc1', self.portal.objectIds())

    def test_copy_multiple_objects(self):
        self.doc2 = self.portal[self.portal.invokeFactory(
            'Document', id='doc2', title='My Document')]
        self.request['BODY'] = '{"source": ["%s", "%s"]}' % (
            self.doc1.absolute_url(), self.doc2.absolute_url())
        service = self.traverse('/plone/@copy', method='POST')
        service()
        self.assertIn('copy_of_doc1', self.portal.objectIds())
        self.assertIn('copy_of_doc2', self.portal.objectIds())

    def test_move_single_object(self):
        self.request['BODY'] = '{"source": "%s"}' % self.doc1.absolute_url()
        service = self.traverse('/plone/folder1/@move', method='POST')
        service()
        self.assertIn('doc1', self.folder1.objectIds())
        self.assertNotIn('doc1', self.portal.objectIds())

    def test_move_multiple_objects(self):
        self.doc2 = self.portal[self.portal.invokeFactory(
            'Document', id='doc2', title='My Document')]
        self.request['BODY'] = '{"source": ["%s", "%s"]}' % (
            self.doc1.absolute_url(), self.doc2.absolute_url())
        service = self.traverse('/plone/folder1/@move', method='POST')
        service()
        self.assertIn('doc1', self.folder1.objectIds())
        self.assertIn('doc2', self.folder1.objectIds())
        self.assertNotIn('doc1', self.portal.objectIds())
        self.assertNotIn('doc2', self.portal.objectIds())

    def test_copy_not_existing_object(self):
        self.request['BODY'] = '{"source": "does-not-exist"}'
        service = self.traverse('/plone/@copy', method='POST')
        res = json.loads(service())
        self.assertEqual([], res)

    def test_get_object_by_intid(self):
        intids = queryUtility(IIntIds)
        service = self.traverse('/plone/@copy', method='POST')
        obj = service.get_object(intids.getId(self.doc1))
        self.assertEqual(self.doc1, obj)

    def test_get_object_by_url(self):
        service = self.traverse('/plone/@copy', method='POST')
        obj = service.get_object(self.doc1.absolute_url())
        self.assertEqual(self.doc1, obj)

    def test_get_object_by_path(self):
        service = self.traverse('/plone/@copy', method='POST')
        obj = service.get_object('/doc1')
        self.assertEqual(self.doc1, obj)

    def test_get_object_by_uid(self):
        service = self.traverse('/plone/@copy', method='POST')
        obj = service.get_object(self.doc1.UID())
        self.assertEqual(self.doc1, obj)

    def test_copy_without_source_raises_400(self):
        service = self.traverse('/plone/@copy', method='POST')
        with self.assertRaises(BadRequest):
            service()
