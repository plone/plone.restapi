# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.expansion import expandable_elements
from zope.component import provideAdapter
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

import unittest


class ExpandableElementFoo(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if expand:
            return {'foo': 'expanded'}
        else:
            return {'foo': 'collapsed'}


class ExpandableElementBar(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if expand:
            return {'bar': 'expanded'}
        else:
            return {'bar': 'collapsed'}


class TestExpansion(unittest.TestCase):

    def setUp(self):
        provideAdapter(
            ExpandableElementFoo,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name='foo'
        )
        provideAdapter(
            ExpandableElementBar,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name='bar'
        )

    def test_expansion_returns_collapsed_elements(self):
        request = TestRequest()
        self.assertEqual({'foo': 'collapsed', 'bar': 'collapsed'},
                         expandable_elements(None, request))

    def test_expansion_returns_expanded_element(self):
        request = TestRequest(form={'expand': 'foo'})
        self.assertEqual({'foo': 'expanded', 'bar': 'collapsed'},
                         expandable_elements(None, request))

    def test_expansion_returns_multiple_expanded_elements(self):
        request = TestRequest(form={'expand': 'foo,bar'})
        self.assertEqual({'foo': 'expanded', 'bar': 'expanded'},
                         expandable_elements(None, request))
