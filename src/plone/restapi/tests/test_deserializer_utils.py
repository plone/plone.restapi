from plone.restapi.deserializer.utils import path2uid
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest


class TestDeserializerUtils(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.workflowTool = getToolByName(self.portal, "portal_workflow")
        self.portal_url = self.portal.absolute_url()
        self.portal.invokeFactory("Document", id="doc1", title="Document 1")
        self.portal.invokeFactory("File", id="file1", title="File 1")

        self.doc_path = "/".join(self.portal.doc1.getPhysicalPath())
        self.file_path = "/".join(self.portal.file1.getPhysicalPath())

    def test_path2uid_base(self):
        self.assertEqual(
            path2uid(context=self.portal, link=self.doc_path),
            "resolveuid/{}".format(self.portal.doc1.UID()),
        )

    def test_path2uid_keep_viewish_suffix(self):
        self.assertEqual(
            path2uid(context=self.portal, link=self.doc_path + "/@@view"),
            "resolveuid/{}/@@view".format(self.portal.doc1.UID()),
        )
        self.assertEqual(
            path2uid(context=self.portal, link=self.file_path + "/@@download/file"),
            "resolveuid/{}/@@download/file".format(self.portal.file1.UID()),
        )

        self.assertEqual(
            path2uid(context=self.portal, link=self.file_path + "/@@display-file/file"),
            "resolveuid/{}/@@display-file/file".format(self.portal.file1.UID()),
        )
