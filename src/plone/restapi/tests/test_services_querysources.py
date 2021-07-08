from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestQuerysourcesEndpoint(unittest.TestCase):

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

        self.doc = api.content.create(
            container=self.portal,
            id="testdoc",
            type="DXTestDocument",
            title="Document 1",
        )
        transaction.commit()

    def test_get_querysource_xxx(self):
        response = self.api_session.get(
            "%s/@querysources/test_choice_with_querysource?query=2"
            % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@querysources/test_choice_with_querysource?query=2",  # noqa
                "items": [{"title": "Title 2", "token": "token2"}],
                "items_total": 1,
            },
        )

    def test_get_querysource_batched(self):
        response = self.api_session.get(
            "%s/@querysources/test_choice_with_querysource?query=token&b_size=1"
            % self.doc.absolute_url()
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "@id": self.doc.absolute_url()
                + "/@querysources/test_choice_with_querysource?query=token",  # noqa
                "batching": {
                    "@id": self.doc.absolute_url()
                    + "/@querysources/test_choice_with_querysource?query=token&b_size=1",  # noqa
                    "first": self.doc.absolute_url()
                    + "/@querysources/test_choice_with_querysource?b_start=0&query=token&b_size=1",  # noqa
                    "last": self.doc.absolute_url()
                    + "/@querysources/test_choice_with_querysource?b_start=2&query=token&b_size=1",  # noqa
                    "next": self.doc.absolute_url()
                    + "/@querysources/test_choice_with_querysource?b_start=1&query=token&b_size=1",  # noqa
                },
                "items": [{"title": "Title 1", "token": "token1"}],
                "items_total": 3,
            },
        )

    def test_querysource_cant_be_enumerated(self):
        response = self.api_session.get(
            "%s/@querysources/test_choice_with_querysource" % self.doc.absolute_url()
        )

        self.assertEqual(400, response.status_code)
        response = response.json()

        self.assertEqual(
            response.get("error"),
            {
                "type": "Bad Request",
                "message": "Enumerating querysources is not supported. "
                "Please search the source using the ?query= QS parameter",
            },
        )

    def test_get_querysource_for_unknown_field(self):
        response = self.api_session.get(
            "%s/@querysources/unknown_field" % self.doc.absolute_url()
        )

        self.assertEqual(404, response.status_code)
        response = response.json()
        self.assertEqual(
            response,
            {
                "error": {
                    "type": "Not Found",
                    "message": "No such field: 'unknown_field'",
                }
            },
        )

    def test_context_querysource_xxx(self):
        self.doc.title = "Foo Bar Baz"
        transaction.commit()

        response = self.api_session.get(
            "%s/@querysources/test_choice_with_context_querysource?query=foo"
            % self.doc.absolute_url()
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "@id": self.portal_url
                + "/testdoc/@querysources/test_choice_with_context_querysource?query=foo",  # noqa
                "items": [{"token": "foo", "title": "Foo"}],
                "items_total": 1,
            },
        )

    def tearDown(self):
        self.api_session.close()
