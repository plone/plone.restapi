from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.typesettings.workflows import suggest_state
from plone.restapi.typesettings.workflows import visibility

import transaction
import unittest


class WorkflowsTestCase(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.workflow_tool = self.portal.portal_workflow
        self.api = RelativeSession(self.portal.absolute_url(), test=self)
        self.api.headers["Accept"] = "application/json"
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def create(self, id, type_id="Document", transition=None):
        self.portal.invokeFactory(type_id, id, title=id)
        if transition:
            self.workflow_tool.doActionFor(self.portal[id], transition)
        transaction.commit()

    def review_state(self, id):
        transaction.begin()
        return self.workflow_tool.getInfoFor(self.portal[id], "review_state", None)


class TestWorkflowsGet(WorkflowsTestCase):
    def test_listing(self):
        response = self.api.get("/@workflows")
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["@id"], self.portal.absolute_url() + "/@workflows")
        self.assertEqual(result["default"], "simple_publication_workflow")
        items = {item["id"]: item for item in result["items"]}
        self.assertEqual(set(items), set(self.workflow_tool.getWorkflowIds()))
        titles = [item["title"] for item in result["items"]]
        self.assertEqual(titles, sorted(titles))
        self.assertEqual(
            items["simple_publication_workflow"],
            {
                "@id": self.portal.absolute_url()
                + "/@workflows/simple_publication_workflow",
                "id": "simple_publication_workflow",
                "title": "Simple Publication Workflow",
                "description": items["simple_publication_workflow"]["description"],
                "initial_state": "private",
                "states": ["pending", "private", "published"],
            },
        )

    def test_no_default(self):
        self.workflow_tool.setDefaultChain("")
        transaction.commit()
        self.assertIsNone(self.api.get("/@workflows").json()["default"])

    def test_item(self):
        response = self.api.get("/@workflows/simple_publication_workflow")
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["initial_state"], "private")
        states = {state["id"]: state for state in result["states"]}
        self.assertEqual(list(states), ["pending", "private", "published"])
        published = states["published"]
        # The test layer renames the state.
        self.assertEqual(published["title"], "Published with accent é")
        self.assertEqual(published["visibility"], "anyone")
        self.assertEqual(sorted(published["transitions"]), ["reject", "retract"])
        self.assertEqual(published["permission_roles"]["View"], ["Anonymous"])
        self.assertEqual(states["private"]["visibility"], "restricted")
        transitions = {item["id"]: item for item in result["transitions"]}
        self.assertEqual(
            transitions["publish"],
            {
                "id": "publish",
                "title": "Publish",
                "description": transitions["publish"]["description"],
                "new_state": "published",
                "guard": {
                    "permissions": ["Review portal content"],
                    "roles": [],
                    "expression": "",
                },
            },
        )
        self.assertIn("Document", result["types"])
        self.assertIn("Event", result["types"])
        self.assertNotIn("Image", result["types"])
        self.assertEqual(result["types"], sorted(result["types"]))

    def test_types_with_an_explicit_chain(self):
        self.workflow_tool.setChainForPortalTypes(("Event",), ("intranet_workflow",))
        transaction.commit()
        result = self.api.get("/@workflows/intranet_workflow").json()
        self.assertEqual(result["types"], ["Event"])
        result = self.api.get("/@workflows/simple_publication_workflow").json()
        self.assertNotIn("Event", result["types"])

    def test_members_visibility(self):
        states = {
            state["id"]: state["visibility"]
            for state in self.api.get("/@workflows/intranet_workflow").json()["states"]
        }
        self.assertEqual(
            states,
            {
                "external": "anyone",
                "internal": "members",
                "internally_published": "members",
                "pending": "members",
                "private": "restricted",
            },
        )

    def test_unknown_workflows_and_paths(self):
        for path in (
            "/@workflows/missing",
            "/@workflows/simple_publication_workflow/extra",
        ):
            self.assertEqual(self.api.get(path).status_code, 404, path)


class TestVisibility(WorkflowsTestCase):
    def state(self, roles):
        state = self.workflow_tool.simple_publication_workflow.states.private
        state.setPermission("View", isinstance(roles, list), roles)
        return state

    def test_visibility(self):
        self.assertEqual(visibility(self.state(("Anonymous",))), "anyone")
        self.assertEqual(visibility(self.state(["Anonymous"])), "anyone")
        self.assertEqual(visibility(self.state(("Authenticated",))), "members")
        self.assertEqual(visibility(self.state(("Owner", "Reviewer"))), "restricted")
        # Acquired, so other roles may see items too.
        self.assertEqual(visibility(self.state(["Member"])), "unknown")
        state = self.state(())
        del state.permission_roles["View"]
        self.assertEqual(visibility(state), "unknown")

    def test_suggestions_keep_visibility(self):
        workflows = self.workflow_tool
        simple = workflows.simple_publication_workflow
        intranet = workflows.intranet_workflow

        def suggest(source, target):
            return {
                state.getId(): suggest_state(state, target)
                for state in source.states.objectValues()
            }

        self.assertEqual(
            suggest(simple, intranet),
            {"private": "private", "pending": "private", "published": "external"},
        )
        # Nothing is less visible than internal, so the least visible state.
        self.assertEqual(
            suggest(intranet, workflows.one_state_workflow),
            dict.fromkeys(intranet.states.objectIds(), "published"),
        )
        self.assertEqual(
            suggest(intranet, simple),
            {
                "external": "published",
                "internal": "private",
                "internally_published": "private",
                "pending": "pending",
                "private": "private",
            },
        )
        # Without a workflow, the initial state of the least visible ones.
        self.assertEqual(suggest_state(None, simple), "private")
        self.assertIsNone(suggest_state(simple.states.private, None))


class TestWorkflowsDefault(WorkflowsTestCase):
    def setUp(self):
        super().setUp()
        self.workflow_tool.setChainForPortalTypes(("Event",), ("intranet_workflow",))
        transaction.commit()
        self.create("private")
        self.create("published", transition="publish")
        self.create("event", "Event")

    def test_dry_run(self):
        response = self.api.post(
            "/@workflows", json={"default": "intranet_workflow", "dry_run": True}
        )
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["workflow"], "intranet_workflow")
        self.assertEqual(result["current"], "simple_publication_workflow")
        self.assertEqual(
            result["states"],
            [
                {"id": "pending", "count": 0, "suggested": "private"},
                {"id": "private", "count": 1, "suggested": "private"},
                {"id": "published", "count": 1, "suggested": "external"},
            ],
        )
        self.assertEqual(result["unaffected"], 0)
        self.assertIn("Document", result["types"])
        self.assertNotIn("Event", result["types"])
        transaction.begin()
        self.assertEqual(
            self.workflow_tool.getDefaultChain(), ("simple_publication_workflow",)
        )

    def test_change_default(self):
        response = self.api.post(
            "/@workflows",
            json={"default": "intranet_workflow", "state_map": {"private": "internal"}},
        )
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(
            response.json(), {"default": "intranet_workflow", "changed": 2}
        )
        transaction.begin()
        self.assertEqual(self.workflow_tool.getDefaultChain(), ("intranet_workflow",))
        self.assertEqual(self.review_state("private"), "internal")
        self.assertEqual(self.review_state("published"), "external")
        # Types with their own workflow keep it.
        self.assertEqual(self.review_state("event"), "internal")
        self.assertNotIn("Document", dict(self.workflow_tool.listChainOverrides()))

    def test_no_default(self):
        response = self.api.post("/@workflows", json={"default": None})
        self.assertEqual(response.status_code, 200, response.text)
        self.assertEqual(response.json(), {"default": None, "changed": 2})
        transaction.begin()
        self.assertEqual(self.workflow_tool.getDefaultChain(), ())
        self.assertEqual(self.workflow_tool.getChainFor("Document"), ())
        response = self.api.post(
            "/@workflows",
            json={"default": "simple_publication_workflow", "dry_run": True},
        )
        self.assertEqual(
            response.json()["states"], [{"id": "", "count": 2, "suggested": "private"}]
        )

    def test_invalid(self):
        for body in (
            {},
            {"default": "missing"},
            {"default": "intranet_workflow", "state_map": {"private": "published"}},
            {"default": "intranet_workflow", "state_map": []},
        ):
            response = self.api.post("/@workflows", json=body)
            self.assertEqual(response.status_code, 400, body)
        self.assertEqual(self.api.post("/@workflows", json=[]).status_code, 400)
        transaction.begin()
        self.assertEqual(
            self.workflow_tool.getDefaultChain(), ("simple_publication_workflow",)
        )


class TestWorkflowsPermissions(WorkflowsTestCase):
    REQUESTS = (
        ("get", "/@workflows"),
        ("get", "/@workflows/simple_publication_workflow"),
        ("post", "/@workflows"),
    )

    def assert_denied(self):
        for method, path in self.REQUESTS:
            response = getattr(self.api, method)(path)
            self.assertIn(response.status_code, (401, 403), (method, path))

    def test_anonymous_is_denied(self):
        self.api.auth = None
        self.assert_denied()

    def test_member_is_denied(self):
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        transaction.commit()
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        self.assert_denied()
