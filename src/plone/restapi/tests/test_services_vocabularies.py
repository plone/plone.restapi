# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getGlobalSiteManager
from zope.component import provideUtility
from zope.componentvocabulary.vocabulary import UtilityTerm
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import six
import transaction
import unittest


TEST_TERM_1 = SimpleTerm(42, token="token1", title=u"Title 1")
TEST_TERM_2 = SimpleTerm(43, token="token2", title=u"Title 2")
TEST_TERM_3 = SimpleTerm(44, token="token3")
TEST_TERM_4 = UtilityTerm(45, "token4")
if six.PY2:
    TEST_TERM_5 = SimpleTerm(46, token="token5", title=u"T\xf6tle 5")
    TEST_TERM_6 = SimpleTerm(47, token="token6", title="T\xc3\xb6tle 6")
else:
    TEST_TERM_5 = SimpleTerm(46, token="token5", title="Tötle 5")
    TEST_TERM_6 = SimpleTerm(47, token="token6", title="Tötle 6")

TEST_VOCABULARY = SimpleVocabulary(
    [TEST_TERM_1, TEST_TERM_2, TEST_TERM_3, TEST_TERM_4, TEST_TERM_5, TEST_TERM_6]
)


def test_vocabulary_factory(context):
    return TEST_VOCABULARY


def test_context_vocabulary_factory(context):
    return SimpleVocabulary(
        [
            SimpleTerm(context.id, token="id", title=context.id),
            SimpleTerm(context.title, token="title", title=context.title),
        ]
    )


class TestVocabularyEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    maxDiff = None

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        provideUtility(
            test_vocabulary_factory,
            provides=IVocabularyFactory,
            name="plone.restapi.tests.test_vocabulary",
        )

    def test_get_vocabulary(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.restapi.tests.test_vocabulary",  # noqa
                u"items": [
                    {u"title": u"Title 1", u"token": u"token1"},
                    {u"title": u"Title 2", u"token": u"token2"},
                    {u"title": u"token3", u"token": u"token3"},
                    {u"title": u"token4", u"token": u"token4"},
                    {u"title": u"T\xf6tle 5", u"token": u"token5"},
                    {u"title": u"T\xf6tle 6", u"token": u"token6"},
                ],
                u"items_total": 6,
            },
        )

    def test_get_vocabulary_batched(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary?b_size=1"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.restapi.tests.test_vocabulary",  # noqa
                u"batching": {
                    u"@id": self.portal_url
                    + u"/@vocabularies/plone.restapi.tests.test_vocabulary?b_size=1",  # noqa
                    u"first": self.portal_url
                    + u"/@vocabularies/plone.restapi.tests.test_vocabulary?b_start=0&b_size=1",  # noqa
                    u"last": self.portal_url
                    + u"/@vocabularies/plone.restapi.tests.test_vocabulary?b_start=5&b_size=1",  # noqa
                    u"next": self.portal_url
                    + u"/@vocabularies/plone.restapi.tests.test_vocabulary?b_start=1&b_size=1",  # noqa
                },
                u"items": [{u"title": u"Title 1", u"token": u"token1"}],
                u"items_total": 6,
            },
        )

    def test_get_vocabulary_filtered_by_title(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary?title=2"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.restapi.tests.test_vocabulary?title=2",  # noqa
                u"items": [{u"title": u"Title 2", u"token": u"token2"}],
                u"items_total": 1,
            },
        )

    def test_get_vocabulary_filtered_by_non_ascii_title(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary?title=t%C3%B6tle"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.restapi.tests.test_vocabulary?title=t%C3%B6tle",  # noqa
                u"items": [
                    {u"title": u"T\xf6tle 5", u"token": u"token5"},
                    {u"title": u"T\xf6tle 6", u"token": u"token6"},
                ],
                u"items_total": 2,
            },
        )

    def test_get_vocabulary_filtered_by_token(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary?token=token1"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.restapi.tests.test_vocabulary?token=token1",  # noqa
                u"items": [{u"title": u"Title 1", u"token": u"token1"}],
                u"items_total": 1,
            },
        )

    def test_get_vocabulary_filtered_by_token_partial_not_match(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary?token=token"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.restapi.tests.test_vocabulary?token=token",  # noqa
                u"items": [],
                u"items_total": 0,
            },
        )

    def test_get_vocabulary_filtered_by_title_and_token_returns_error(self):
        response = self.api_session.get(
            "/@vocabularies/plone.restapi.tests.test_vocabulary?token=token1&title=Title"  # noqa
        )

        self.assertEqual(400, response.status_code)
        response = response.json()
        self.assertEqual(
            response.get("error"),
            {
                u"message": u"You can not filter by title and token at the same time.",  # noqa
                u"type": u"Invalid parameters",
            },
        )

    def test_get_corner_case_vocabulary_filtered_by_token(self):
        response = self.api_session.get(
            "/@vocabularies/plone.app.vocabularies.Weekdays?token=0"
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                u"@id": self.portal_url
                + u"/@vocabularies/plone.app.vocabularies.Weekdays?token=0",  # noqa
                u"items": [{"title": "Monday", "token": "0"}],
                u"items_total": 1,
            },
        )

    def test_get_unknown_vocabulary(self):
        response = self.api_session.get("/@vocabularies/unknown.vocabulary")

        self.assertEqual(404, response.status_code)
        response = response.json()

        self.assertEqual(
            response,
            {
                u"error": {
                    u"type": u"Not Found",
                    u"message": u"The vocabulary 'unknown.vocabulary' does not exist",
                }
            },
        )

    def test_get_all_vocabularies(self):
        response = self.api_session.get("/@vocabularies")

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertTrue(len(response) > 0)
        self.assertTrue("@id" in list(response[0]))
        self.assertTrue("title" in list(response[0]))
        self.assertEqual(
            [
                {
                    u"@id": self.portal_url
                    + u"/@vocabularies/plone.restapi.tests.test_vocabulary",  # noqa
                    u"title": u"plone.restapi.tests.test_vocabulary",
                }
            ],
            [
                x
                for x in response
                if x.get("title") == "plone.restapi.tests.test_vocabulary"
            ],
        )

    def test_context_vocabulary(self):
        api.content.create(
            container=self.portal, id="testdoc", type="Document", title=u"Document 1"
        )
        transaction.commit()

        context_vocab_name = "plone.restapi.tests.test_context_vocabulary"
        provideUtility(
            test_context_vocabulary_factory,
            provides=IVocabularyFactory,
            name=context_vocab_name,
        )

        response = self.api_session.get(
            "testdoc/@vocabularies/{}".format(context_vocab_name)
        )

        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(provided=IVocabularyFactory, name=context_vocab_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                u"@id": self.portal_url
                + u"/testdoc/@vocabularies/plone.restapi.tests.test_context_vocabulary",  # noqa
                u"items": [
                    {u"title": u"testdoc", u"token": u"id"},
                    {u"title": u"Document 1", u"token": u"title"},
                ],
                u"items_total": 2,
            },
        )

    def tearDown(self):
        self.api_session.close()
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(
            provided=IVocabularyFactory, name="plone.restapi.tests.test_vocabulary"
        )
