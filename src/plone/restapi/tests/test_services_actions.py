from plone import api
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore import permissions
from Products.CMFCore.ActionInformation import Action
from Products.CMFCore.ActionInformation import ActionCategory

import transaction
import unittest


TEST_CATEGORY_ID = "testcategory"


class TestActions(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def add_category(self, name):
        category = ActionCategory()
        category.id = name
        self.portal_actions._setObject(name, category)
        return category

    def add_action(
        self, category, name, title, icon_expr="", available_expr="", permissions=()
    ):
        action = Action(
            name,
            title=title,
            icon_expr=icon_expr,
            available_expr=available_expr,
            permissions=permissions,
        )
        action.id = name
        category._setObject(name, action)
        return action

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.anon_api_session = RelativeSession(self.portal_url)
        self.anon_api_session.headers.update({"Accept": "application/json"})

        self.portal_actions = api.portal.get_tool(name="portal_actions")
        existing_ids = self.portal_actions.objectIds()
        self.portal_actions.manage_delObjects(ids=existing_ids)
        self.cat1 = self.add_category("category1")
        self.add_action(
            self.cat1,
            "member_action",
            "Members only",
            available_expr="python:member is not None",
        )
        self.add_action(
            self.cat1,
            "view_action",
            "Action with view permission",
            permissions=(permissions.View,),
        )
        self.add_action(
            self.cat1,
            "manage_action",
            "Action with Manage Portal Content permission",
            permissions=(permissions.ManagePortal,),
        )
        self.cat2 = self.add_category("category2")
        self.cat3 = self.add_category("category3")

        transaction.commit()

    def tearDown(self):
        self.api_session.close()
        self.anon_api_session.close()

    def test_actions_all_categories(self):
        response = self.api_session.get("/@actions")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(["category1", "category2", "category3"], sorted(response))

    def test_actions_selected_categories(self):
        response = self.api_session.get(
            "/@actions?categories:list=category1&categories:list=category2"
        )

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(["category1", "category2"], sorted(response))

    def test_actions_siteroot(self):
        response = self.api_session.get("/@actions")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(
            response,
            {
                "category1": [
                    {"title": "Members only", "id": "member_action", "icon": ""},
                    {
                        "title": "Action with view permission",
                        "id": "view_action",
                        "icon": "",
                    },
                    {
                        "title": "Action with Manage Portal Content permission",
                        "id": "manage_action",
                        "icon": "",
                    },
                ],
                "category2": [],
                "category3": [],
            },
        )

    def test_actions_siteroot_anon(self):
        response = self.anon_api_session.get("/@actions")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(
            response,
            {
                "category1": [
                    {
                        "title": "Action with view permission",
                        "id": "view_action",
                        "icon": "",
                    }
                ],
                "category2": [],
                "category3": [],
            },
        )

    def test_actions_on_content_object(self):
        self.portal.invokeFactory("Document", id="doc1", title="My Document")
        # we need the category in portal_actions to get additional actions
        # from portal_types
        self.cat_object = self.add_category("object")
        transaction.commit()
        url = "%s/@actions" % self.portal.doc1.absolute_url()
        response = self.api_session.get(url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        object_action_ids = [action["id"] for action in response["object"]]
        self.assertTrue("view" in object_action_ids)
        self.assertTrue("edit" in object_action_ids)

    def test_actions_on_content_object_anon(self):
        self.portal.invokeFactory("Document", id="doc1", title="My Document")
        api.content.transition(obj=self.portal.doc1, transition="publish")
        # we need the category in portal_actions to get additional actions
        # from portal_types
        self.cat_object = self.add_category("object")
        transaction.commit()
        url = "%s/@actions" % self.portal.doc1.absolute_url()
        response = self.anon_api_session.get(url)
        self.assertEqual(response.status_code, 200)
        response = response.json()
        object_action_ids = [action["id"] for action in response["object"]]
        self.assertTrue("view" in object_action_ids)
        self.assertTrue("edit" not in object_action_ids)
