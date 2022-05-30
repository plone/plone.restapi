from plone.restapi.serializer.utils import uid_to_url
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest


class TestSerializerUtils(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.workflowTool = getToolByName(self.portal, "portal_workflow")
        self.portal_url = self.portal.absolute_url()
        self.portal.invokeFactory("Document", id="doc1", title="Document 1")
        self.portal.invokeFactory("File", id="file1", title="File 1")

    def test_uid_to_url_base(self):
        self.assertEqual(
            uid_to_url("resolveuid/{}".format(self.portal.doc1.UID())),
            "{}/doc1".format(self.portal_url),
        )

    def test_uid_to_url_keep_suffix(self):
        self.assertEqual(
            uid_to_url("resolveuid/{}/foo/bar".format(self.portal.doc1.UID())),
            "{}/doc1/foo/bar".format(self.portal_url),
        )

        self.assertEqual(
            uid_to_url("resolveuid/{}/@@download/file".format(self.portal.file1.UID())),
            "{}/file1/@@download/file".format(self.portal_url),
        )

    def test_uid_to_url_does_not_convert_if_there_is_querystring(self):
        self.assertNotEqual(
            uid_to_url("resolveuid/{}?foo=bar".format(self.portal.doc1.UID())),
            "{}/doc1?foo=bar".format(self.portal_url),
        )
        self.assertEqual(
            uid_to_url("resolveuid/{}?foo=bar".format(self.portal.doc1.UID())),
            "resolveuid/{}?foo=bar".format(self.portal.doc1.UID()),
        )

    def test_uid_to_url_do_nothing_if_invalid_path(self):
        self.assertEqual(uid_to_url("/foo/bar"), "/foo/bar")

    def test_uid_to_url_do_nothing_if_external_url(self):
        self.assertEqual(uid_to_url("https://www.plone.org"), "https://www.plone.org")
