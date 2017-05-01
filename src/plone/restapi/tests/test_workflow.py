# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from ZPublisher.pubevents import PubStart
from base64 import b64encode
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import login
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest import TestCase
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.event import notify


class TestWorkflowInfo(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.doc1 = self.portal[self.portal.invokeFactory(
            'Document', id='doc1', title='Test Document')]
        wftool = getToolByName(self.portal, 'portal_workflow')
        wftool.doActionFor(self.portal.doc1, 'submit')
        wftool.doActionFor(self.portal.doc1, 'publish')

    def test_workflow_info_includes_history(self):
        wfinfo = getMultiAdapter((self.doc1, self.request),
                                 name=u'GET_application_json_@workflow')
        info = wfinfo.reply()
        self.assertIn('history', info)
        history = info['history']
        self.assertEqual(3, len(history))
        self.assertEqual('published', history[-1][u'review_state'])
        self.assertEqual('Published', history[-1][u'title'])

    def test_workflow_info_includes_transitions(self):
        wfinfo = getMultiAdapter((self.doc1, self.request),
                                 name=u'GET_application_json_@workflow')
        info = wfinfo.reply()
        self.assertIn('transitions', info)
        transitions = info['transitions']
        self.assertEqual(2, len(transitions))


class TestWorkflowTransition(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.wftool = getToolByName(self.portal, 'portal_workflow')
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory('Document', id='doc1')

    def traverse(self, path='/plone', accept='application/json',
                 method='POST'):
        request = self.layer['request']
        request.environ['PATH_INFO'] = path
        request.environ['PATH_TRANSLATED'] = path
        request.environ['HTTP_ACCEPT'] = accept
        request.environ['REQUEST_METHOD'] = method
        request._auth = 'Basic %s' % b64encode(
            '%s:%s' % (SITE_OWNER_NAME, SITE_OWNER_PASSWORD))
        notify(PubStart(request))
        return request.traverse(path)

    def test_transition_action_succeeds(self):
        service = self.traverse('/plone/doc1/@workflow/publish')
        res = service.reply()
        self.assertEqual(u'published', res[u'review_state'])
        self.assertEqual(
            u'published',
            self.wftool.getInfoFor(self.portal.doc1, u'review_state'))

    def test_calling_endpoint_without_transition_gives_400(self):
        service = self.traverse('/plone/doc1/@workflow')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual('Missing transition', res['error']['message'])

    def test_calling_workflow_with_additional_path_segments_results_in_404(
            self):
        with self.assertRaises(NotFound):
            self.traverse('/plone/doc1/@workflow/publish/test')

    def test_transition_with_comment(self):
        self.request['BODY'] = '{"comment": "A comment"}'
        service = self.traverse('/plone/doc1/@workflow/publish')
        res = service.reply()
        self.assertEqual(u'A comment', res[u'comments'])

    def test_transition_with_invalid_body(self):
        self.request['BODY'] = '{"comment": "A comment", "test": "123"}'
        service = self.traverse('/plone/doc1/@workflow/publish')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual('Invalid body', res['error']['message'])

    def test_invalid_transition_results_in_400(self):
        service = self.traverse('/plone/doc1/@workflow/foo')
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual('WorkflowException', res['error']['type'])
