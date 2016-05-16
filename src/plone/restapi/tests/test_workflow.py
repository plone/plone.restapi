# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import getMultiAdapter


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
                                 name=u'GET_application_json_workflow')
        info = wfinfo.render()
        self.assertIn('history', info)
        history = info['history']
        self.assertEqual(3, len(history))
        self.assertEqual('published', history[-1][u'review_state'])

    def test_workflow_info_includes_transitions(self):
        wfinfo = getMultiAdapter((self.doc1, self.request),
                                 name=u'GET_application_json_workflow')
        info = wfinfo.render()
        self.assertIn('transitions', info)
        transitions = info['transitions']
        self.assertEqual(2, len(transitions))
