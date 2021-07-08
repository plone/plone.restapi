from base64 import b64encode
from DateTime import DateTime
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_WORKFLOWS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName
from unittest import TestCase
from zExceptions import NotFound
from zope.component import getMultiAdapter
from zope.event import notify
from ZPublisher.pubevents import PubStart


class TestWorkflowInfo(TestCase):

    layer = PLONE_RESTAPI_WORKFLOWS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc1", title="Test Document"
            )
        ]
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.doc1, "submit")
        wftool.doActionFor(self.portal.doc1, "publish")

    def test_workflow_info_includes_history(self):
        wfinfo = getMultiAdapter(
            (self.doc1, self.request), name="GET_application_json_@workflow"
        )
        info = wfinfo.reply()
        self.assertIn("history", info)
        history = info["history"]
        self.assertEqual(3, len(history))
        self.assertEqual("published", history[-1]["review_state"])
        self.assertEqual("Published with accent é", history[-1]["title"])

    def test_workflow_info_includes_current_state(self):
        wfinfo = getMultiAdapter(
            (self.doc1, self.request), name="GET_application_json_@workflow"
        )
        info = wfinfo.reply()
        self.assertIn("state", info)
        state = info["state"]
        self.assertEqual(2, len(state))
        self.assertEqual("published", state["id"])
        self.assertEqual("Published with accent é", state["title"])

    def test_workflow_info_unauthorized_history(self):
        login(self.portal, SITE_OWNER_NAME)
        doc2 = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument", id="doc2", title="Test Document"
            )
        ]
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(doc2, "submit")
        wftool.doActionFor(doc2, "publish")
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, TEST_USER_NAME)
        wfinfo = getMultiAdapter(
            (doc2, self.request), name="GET_application_json_@workflow"
        )
        info = wfinfo.reply()
        self.assertIn("history", info)
        history = info["history"]
        self.assertEqual(0, len(history))

    def test_workflow_info_includes_transitions(self):
        wfinfo = getMultiAdapter(
            (self.doc1, self.request), name="GET_application_json_@workflow"
        )
        info = wfinfo.reply()
        self.assertIn("transitions", info)
        transitions = info["transitions"]
        self.assertEqual(2, len(transitions))

    def test_collapsed_workflow_info_in_content_serialization(self):
        serializer = getMultiAdapter((self.doc1, self.request), ISerializeToJson)
        obj = serializer()
        self.assertIn("workflow", obj["@components"])
        self.assertIn("@id", obj["@components"]["workflow"])

    def test_expanded_workflow_info_in_content_serialization(self):
        self.request.form.update({"expand": "workflow"})
        serializer = getMultiAdapter((self.doc1, self.request), ISerializeToJson)
        obj = serializer()
        self.assertIn("workflow", obj["@components"])
        self.assertIn("transitions", obj["@components"]["workflow"])
        self.assertIn("history", obj["@components"]["workflow"])

    def test_workflow_info_empty_on_siteroot(self):
        wfinfo = getMultiAdapter(
            (self.portal, self.request), name="GET_application_json_@workflow"
        )
        obj = wfinfo.reply()

        self.assertEqual(obj["transitions"], [])
        self.assertEqual(obj["history"], [])


class TestWorkflowTransition(TestCase):

    layer = PLONE_RESTAPI_WORKFLOWS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.wftool = getToolByName(self.portal, "portal_workflow")
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Document", id="doc1")

    def traverse(
        self, path="/plone", accept="application/json", method="POST", auth=None
    ):
        request = self.layer["request"]
        request.environ["PATH_INFO"] = path
        request.environ["PATH_TRANSLATED"] = path
        request.environ["HTTP_ACCEPT"] = accept
        request.environ["REQUEST_METHOD"] = method
        if auth is None:
            auth = f"{SITE_OWNER_NAME}:{SITE_OWNER_PASSWORD}"
        request._auth = "Basic %s" % b64encode(auth.encode("utf8")).decode("utf8")
        notify(PubStart(request))
        return request.traverse(path)

    def test_transition_action_succeeds(self):
        service = self.traverse("/plone/doc1/@workflow/publish")
        res = service.reply()
        self.assertEqual("published", res["review_state"])
        self.assertEqual(
            "published", self.wftool.getInfoFor(self.portal.doc1, "review_state")
        )

    def test_transition_action_succeeds_changes_effective(self):
        doc1 = self.portal.doc1
        self.assertEqual(doc1.effective_date, None)
        now = DateTime()
        service = self.traverse("/plone/doc1/@workflow/publish")
        service.reply()
        self.assertTrue(isinstance(doc1.effective_date, DateTime))
        self.assertTrue(doc1.effective_date >= now)

    def test_calling_endpoint_without_transition_gives_400(self):
        service = self.traverse("/plone/doc1/@workflow")
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual("Missing transition", res["error"]["message"])

    def test_calling_workflow_with_additional_path_segments_results_in_404(self):
        with self.assertRaises(NotFound):
            self.traverse("/plone/doc1/@workflow/publish/test")

    def test_transition_with_comment(self):
        self.request["BODY"] = '{"comment": "A comment"}'
        service = self.traverse("/plone/doc1/@workflow/publish")
        res = service.reply()
        self.assertEqual("A comment", res["comments"])

    def test_transition_including_children(self):
        folder = self.portal[self.portal.invokeFactory("Folder", id="folder")]
        subfolder = folder[folder.invokeFactory("Folder", id="subfolder")]
        self.request["BODY"] = '{"comment": "A comment", "include_children": true}'
        service = self.traverse("/plone/folder/@workflow/publish")
        service.reply()
        self.assertEqual(200, self.request.response.getStatus())
        self.assertEqual("published", self.wftool.getInfoFor(folder, "review_state"))
        self.assertEqual("published", self.wftool.getInfoFor(subfolder, "review_state"))

    def test_transition_with_effective_date(self):
        self.request["BODY"] = '{"effective": "2018-06-24T09:17:02"}'
        service = self.traverse("/plone/doc1/@workflow/publish")
        service.reply()
        self.assertEqual(
            "2018-06-24T09:17:00+00:00", self.portal.doc1.effective().ISO8601()
        )

    def test_transition_with_expiration_date(self):
        self.request["BODY"] = '{"expires": "2019-06-20T18:00:00"}'
        service = self.traverse("/plone/doc1/@workflow/publish")
        service.reply()
        self.assertEqual(
            "2019-06-20T18:00:00+00:00", self.portal.doc1.expires().ISO8601()
        )

    def test_invalid_transition_results_in_400(self):
        service = self.traverse("/plone/doc1/@workflow/foo")
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual("WorkflowException", res["error"]["type"])

    def test_invalid_effective_date_results_in_400(self):
        self.request["BODY"] = '{"effective": "now"}'
        service = self.traverse("/plone/doc1/@workflow/publish")
        res = service.reply()
        self.assertEqual(400, self.request.response.getStatus())
        self.assertEqual("Bad Request", res["error"]["type"])

    def test_transition_with_no_access_to_review_history_in_target_state(self):
        self.wftool.setChainForPortalTypes(["Folder"], "restriction_workflow")
        self.portal[self.portal.invokeFactory("Folder", id="folder", title="Test")]
        setRoles(
            self.portal, TEST_USER_ID, ["Contributor", "Editor", "Member", "Reviewer"]
        )
        login(self.portal, TEST_USER_NAME)

        auth = f"{TEST_USER_NAME}:{TEST_USER_PASSWORD}"
        service = self.traverse("/plone/folder/@workflow/restrict", auth=auth)
        res = service.reply()

        self.assertEqual(200, self.request.response.getStatus(), res)
        self.assertEqual("restricted", res["review_state"], res)
