from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestSourcesEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    maxDiff = None

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.doc = api.content.create(
            container=self.portal,
            id="testdoc",
            type="DXTestDocument",
            title="Document 1",
        )
        transaction.commit()

    def test_get_source(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_source" % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@sources/test_choice_with_source",  # noqa
                "items": [
                    {"title": "Title 1", "token": "token1"},
                    {"title": "Title 2", "token": "token2"},
                    {"title": "Title 3", "token": "token3"},
                ],
                "items_total": 3,
            },
        )

    def test_get_source_batched(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_source?b_size=1" % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@sources/test_choice_with_source",  # noqa
                "batching": {
                    "@id": self.doc.absolute_url()
                    + "/@sources/test_choice_with_source?b_size=1",  # noqa
                    "first": self.doc.absolute_url()
                    + "/@sources/test_choice_with_source?b_start=0&b_size=1",  # noqa
                    "last": self.doc.absolute_url()
                    + "/@sources/test_choice_with_source?b_start=2&b_size=1",  # noqa
                    "next": self.doc.absolute_url()
                    + "/@sources/test_choice_with_source?b_start=1&b_size=1",  # noqa
                },
                "items": [{"title": "Title 1", "token": "token1"}],
                "items_total": 3,
            },
        )

    def test_get_source_filtered_by_title(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_source?title=2" % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@sources/test_choice_with_source?title=2",  # noqa
                "items": [{"title": "Title 2", "token": "token2"}],
                "items_total": 1,
            },
        )

    def test_get_source_filtered_by_token(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_source?token=token1" % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@sources/test_choice_with_source?token=token1",  # noqa
                "items": [{"title": "Title 1", "token": "token1"}],
                "items_total": 1,
            },
        )

    def test_get_source_filtered_by_token_partial_not_match(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_source?token=token" % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@sources/test_choice_with_source?token=token",  # noqa
                "items": [],
                "items_total": 0,
            },
        )

    def test_get_source_filtered_by_title_and_token_returns_error(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_source?token=token1&title=Title"
            % self.doc.absolute_url()  # noqa
        )

        self.assertEqual(400, response.status_code)
        response = response.json()
        self.assertEqual(
            response.get("error"),
            {
                "type": "Invalid parameters",
                "message": "You can not filter by title and token at the same time.",  # noqa
            },
        )

    def test_get_non_iterable_source_returns_error(self):
        response = self.api_session.get(
            "%s/@sources/test_choice_with_non_iterable_source" % self.doc.absolute_url()
        )

        self.assertEqual(400, response.status_code)
        response = response.json()
        self.assertEqual(
            response.get("error"),
            {
                "type": "Bad Request",
                "message": "Source for field 'test_choice_with_non_iterable_source' is not iterable. ",
            },
        )

    def test_get_source_for_unknown_field(self):
        response = self.api_session.get(
            "%s/@sources/unknown_field" % self.doc.absolute_url()
        )

        self.assertEqual(404, response.status_code)
        response = response.json()

        self.assertEqual(
            response.get("error"),
            {"type": "Not Found", "message": "No such field: 'unknown_field'"},
        )

    def test_context_source(self):
        self.doc.title = "Foo Bar Baz"
        transaction.commit()

        response = self.api_session.get(
            "%s/@sources/test_choice_with_context_source" % self.doc.absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url
                + "/testdoc/@sources/test_choice_with_context_source",  # noqa
                "items": [
                    {"token": "foo", "title": "Foo"},
                    {"token": "bar", "title": "Bar"},
                    {"token": "baz", "title": "Baz"},
                ],
                "items_total": 3,
            },
        )

    def test_source_filtered_by_non_ascii_title(self):
        self.doc.title = "Bär"
        transaction.commit()

        response = self.api_session.get(
            "%s/@sources/test_choice_with_context_source?title=b%%C3%%A4r"
            % self.doc.absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url
                + "/testdoc/@sources/test_choice_with_context_source?title=b%C3%A4r",  # noqa
                "items": [{"token": "b=C3=A4r", "title": "B\xe4r"}],
                "items_total": 1,
            },
        )

    def tearDown(self):
        self.api_session.close()
