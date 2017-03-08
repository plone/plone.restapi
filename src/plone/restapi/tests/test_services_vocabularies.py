# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import provideUtility
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary
from zope.schema.vocabulary import SimpleTerm

import transaction
import unittest


TEST_TERM_1 = SimpleTerm(42, token='token1', title=u'Title 1')
TEST_TERM_2 = SimpleTerm(43, token='token2', title=u'Title 2')
TEST_VOCABULARY = SimpleVocabulary([TEST_TERM_1, TEST_TERM_2])


def test_vocabulary_factory(context):
    return TEST_VOCABULARY


def test_context_vocabulary_factory(context):
    return SimpleVocabulary([
        SimpleTerm(context.id, token='id', title=context.id),
        SimpleTerm(context.title, token='title', title=context.title)
    ])


class TestVocabularyEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    maxDiff = None

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        provideUtility(
            test_vocabulary_factory,
            provides=IVocabularyFactory,
            name='plone.restapi.tests.test_vocabulary'
        )

    def test_get_vocabulary(self):
        response = self.api_session.get(
            '/@vocabularies/plone.restapi.tests.test_vocabulary'
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {u'@id': u'http://localhost:55001/plone/@vocabularies/''plone.restapi.tests.test_vocabulary',  # noqa
             u'terms': [
                 {u'@id': u'http://localhost:55001/plone/@vocabularies/plone.restapi.tests.test_vocabulary/token1',  # noqa
                  u'title': u'Title 1',
                  u'token': u'token1'},
                 {u'@id': u'http://localhost:55001/plone/@vocabularies/plone.restapi.tests.test_vocabulary/token2',  # noqa
                  u'title': u'Title 2',
                  u'token': u'token2'}]})

    def test_get_unknown_vocabulary(self):
        response = self.api_session.get(
            '/@vocabularies/unknown.vocabulary')

        self.assertEqual(404, response.status_code)
        response = response.json()
        self.assertEqual(response['error']['type'], u"Not Found")

    def test_get_all_vocabularies(self):
        response = self.api_session.get('/@vocabularies')

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertTrue(len(response) > 0)
        self.assertTrue(
            '@id' in response[0].keys()
        )
        self.assertTrue(
            'title' in response[0].keys()
        )
        self.assertEqual(
            [
                {
                    u'@id': u'http://localhost:55001/plone/@vocabularies/plone.restapi.tests.test_vocabulary',  # noqa
                    u'title': u'plone.restapi.tests.test_vocabulary'
                }
            ],
            [
                x for x in response
                if x.get('title') == 'plone.restapi.tests.test_vocabulary'
            ]
        )

    def test_context_vocabulary(self):
        api.content.create(
            container=self.portal,
            id="testdoc",
            type='Document',
            title=u'Document 1',
        )
        transaction.commit()

        context_vocab_name = 'plone.restapi.tests.test_context_vocabulary'
        provideUtility(test_context_vocabulary_factory,
                       provides=IVocabularyFactory,
                       name=context_vocab_name)

        response = self.api_session.get(
            'testdoc/@vocabularies/{}'.format(context_vocab_name))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                u'@id': u'http://localhost:55001/plone/testdoc/@vocabularies/plone.restapi.tests.test_context_vocabulary',  # noqa
                u'terms': [
                    {u'@id': u'http://localhost:55001/plone/testdoc/@vocabularies/plone.restapi.tests.test_context_vocabulary/id',  # noqa
                     u'title': u'testdoc',
                     u'token': u'id'},
                    {u'@id': u'http://localhost:55001/plone/testdoc/@vocabularies/plone.restapi.tests.test_context_vocabulary/title',  # noqa
                     u'title': u'Document 1',
                     u'token': u'title'}]
            })
