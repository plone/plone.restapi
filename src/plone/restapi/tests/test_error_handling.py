"""
Test error handling in the Rest API.
"""

from plone.restapi import testing
from Products.Five.browser import BrowserView
from zope.component import provideAdapter
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import json
import transaction
import unittest


class InternalServerErrorView(BrowserView):
    def __call__(self):  # pragma: no cover
        from urllib.error import HTTPError

        raise HTTPError(
            "http://nohost/plone/internal_server_error",
            500,
            "InternalServerError",
            {},
            None,
        )


class TestErrorHandling(testing.PloneRestAPIBrowserTestCase):
    """
    Test error handling in the Rest API.
    """

    def setUp(self):
        """
        Create content instances to test against.
        """
        super().setUp()

        self.portal.invokeFactory("Document", id="document1")
        self.document = self.portal.document1
        self.document_url = self.document.absolute_url()
        self.portal.invokeFactory("Folder", id="folder1")
        self.folder = self.portal.folder1
        self.folder_url = self.folder.absolute_url()
        transaction.commit()

    @unittest.skip("Not working since we moved to plone.rest")
    def test_404_not_found(self):
        response = self.api_session.get("non-existing-resource")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Accept: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertTrue(json.loads(response.content))
        self.assertEqual("NotFound", response.json()["type"])

    @unittest.skip("Not working since we moved to plone.rest")
    def test_401_unauthorized(self):
        response = self.api_session.get(self.document_url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Accept: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertTrue(json.loads(response.content))
        self.assertEqual("Unauthorized", response.json()["type"])

    @unittest.skip("Not working since we moved to plone.rest")
    def test_500_internal_server_error(self):
        provideAdapter(
            InternalServerErrorView,
            adapts=(Interface, IBrowserRequest),
            provides=Interface,
            name="internal_server_error",
        )
        transaction.commit()

        response = self.api_session.get("internal_server_error")

        self.assertEqual(response.status_code, 500)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json",
            "When sending a GET request with Accept: application/json "
            + "the server should respond with sending back application/json.",
        )
        self.assertTrue(json.loads(response.content))
        self.assertEqual("HTTPError", response.json()["type"])
