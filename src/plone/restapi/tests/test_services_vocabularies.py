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

import transaction
import unittest


TEST_TERM_1 = SimpleTerm(42, token="token1", title="Title 1")
TEST_TERM_2 = SimpleTerm(43, token="token2", title="Title 2")
TEST_TERM_3 = SimpleTerm(44, token="token3")
TEST_TERM_4 = UtilityTerm(45, "token4")
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
                "@id": self.portal_url
                + "/@vocabularies/plone.restapi.tests.test_vocabulary",  # noqa
                "items": [
                    {"title": "Title 1", "token": "token1"},
                    {"title": "Title 2", "token": "token2"},
                    {"title": "token3", "token": "token3"},
                    {"title": "token4", "token": "token4"},
                    {"title": "T\xf6tle 5", "token": "token5"},
                    {"title": "T\xf6tle 6", "token": "token6"},
                ],
                "items_total": 6,
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
                "@id": self.portal_url
                + "/@vocabularies/plone.restapi.tests.test_vocabulary",  # noqa
                "batching": {
                    "@id": self.portal_url
                    + "/@vocabularies/plone.restapi.tests.test_vocabulary?b_size=1",  # noqa
                    "first": self.portal_url
                    + "/@vocabularies/plone.restapi.tests.test_vocabulary?b_start=0&b_size=1",  # noqa
                    "last": self.portal_url
                    + "/@vocabularies/plone.restapi.tests.test_vocabulary?b_start=5&b_size=1",  # noqa
                    "next": self.portal_url
                    + "/@vocabularies/plone.restapi.tests.test_vocabulary?b_start=1&b_size=1",  # noqa
                },
                "items": [{"title": "Title 1", "token": "token1"}],
                "items_total": 6,
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
                "@id": self.portal_url
                + "/@vocabularies/plone.restapi.tests.test_vocabulary?title=2",  # noqa
                "items": [{"title": "Title 2", "token": "token2"}],
                "items_total": 1,
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
                "@id": self.portal_url
                + "/@vocabularies/plone.restapi.tests.test_vocabulary?title=t%C3%B6tle",  # noqa
                "items": [
                    {"title": "T\xf6tle 5", "token": "token5"},
                    {"title": "T\xf6tle 6", "token": "token6"},
                ],
                "items_total": 2,
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
                "@id": self.portal_url
                + "/@vocabularies/plone.restapi.tests.test_vocabulary?token=token1",  # noqa
                "items": [{"title": "Title 1", "token": "token1"}],
                "items_total": 1,
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
                "@id": self.portal_url
                + "/@vocabularies/plone.restapi.tests.test_vocabulary?token=token",  # noqa
                "items": [],
                "items_total": 0,
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
                "message": "You can not filter by title and token at the same time.",  # noqa
                "type": "Invalid parameters",
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
                "@id": self.portal_url
                + "/@vocabularies/plone.app.vocabularies.Weekdays?token=0",  # noqa
                "items": [{"title": "Monday", "token": "0"}],
                "items_total": 1,
            },
        )

    def test_get_unknown_vocabulary(self):
        response = self.api_session.get("/@vocabularies/unknown.vocabulary")

        self.assertEqual(404, response.status_code)
        response = response.json()

        self.assertEqual(
            response,
            {
                "error": {
                    "type": "Not Found",
                    "message": "The vocabulary 'unknown.vocabulary' does not exist",
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
                    "@id": self.portal_url
                    + "/@vocabularies/plone.restapi.tests.test_vocabulary",  # noqa
                    "title": "plone.restapi.tests.test_vocabulary",
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
            container=self.portal, id="testdoc", type="Document", title="Document 1"
        )
        transaction.commit()

        context_vocab_name = "plone.restapi.tests.test_context_vocabulary"
        provideUtility(
            test_context_vocabulary_factory,
            provides=IVocabularyFactory,
            name=context_vocab_name,
        )

        response = self.api_session.get(f"testdoc/@vocabularies/{context_vocab_name}")

        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(provided=IVocabularyFactory, name=context_vocab_name)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url
                + "/testdoc/@vocabularies/plone.restapi.tests.test_context_vocabulary",  # noqa
                "items": [
                    {"title": "testdoc", "token": "id"},
                    {"title": "Document 1", "token": "title"},
                ],
                "items_total": 2,
            },
        )

    def tearDown(self):
        self.api_session.close()
        gsm = getGlobalSiteManager()
        gsm.unregisterUtility(
            provided=IVocabularyFactory, name="plone.restapi.tests.test_vocabulary"
        )
