# -*- coding: utf-8 -*-
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestDexteritySerializers(TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_document(self):
        document = createContentInContainer(
            self.portal, u'Document',
            text=IRichText['text'].fromUnicode(u'<p>Some Text</p>'))

        self.maxDiff = None

        # XXX: We use assertDictContainsSubset in order not to have the
        # Plone 5 tests fail because the automatic ID generation for the
        # stock 'Document' type works differently in Plone 5 than Plone 4.

        # A better solution for this (to get stable test behavior across Plone
        # versions) is to create our own FTIs for tests instead of using the
        # stock types from Plone (which may be named the same, but behave
        # differently).

        self.assertDictContainsSubset(
            {
                '@context': 'http://www.w3.org/ns/hydra/context.jsonld',
                '@id': 'http://localhost:55001/plone/document',
                '@type': 'Document',
                'parent': {'@id': 'http://localhost:55001/plone',
                           'description': '',
                           'title': u'Plone site'},
                u'allow_discussion': None,
                u'changeNote': u'',
                u'contributors': [],
                u'creators': [u'test_user_1_'],
                u'description': u'',
                u'effective': None,
                u'exclude_from_nav': False,
                u'expires': None,
                u'language': u'',
                u'relatedItems': [],
                u'rights': u'',
                u'subjects': [],
                u'table_of_contents': None,
                u'text': u'<p>Some Text</p>',
                u'title': u'',
            },
            ISerializeToJson(document))
