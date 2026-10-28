from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestBehaviorsGet(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.api = RelativeSession(self.portal.absolute_url(), test=self)
        self.api.headers["Accept"] = "application/json"
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def items(self):
        response = self.api.get("/@behaviors")
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["@id"], self.portal.absolute_url() + "/@behaviors")
        self.assertEqual(result["items_total"], len(result["items"]))
        return {item["name"]: item for item in result["items"]}

    def test_every_behavior_once_by_name(self):
        items = self.items()
        self.assertIn("plone.dublincore", items)
        self.assertNotIn("plone.app.dexterity.behaviors.metadata.IDublinCore", items)
        self.assertEqual(sorted(items), list(items))

    def test_fields_by_fieldset(self):
        items = self.items()
        self.assertEqual(
            items["plone.leadimage"],
            {
                "name": "plone.leadimage",
                "title": "Lead Image",
                "description": "Adds image and image caption fields",
                "fieldsets": [
                    {
                        "id": "default",
                        "title": "Default",
                        "fields": ["image", "image_caption"],
                    }
                ],
            },
        )
        fieldsets = {
            fieldset["id"]: fieldset["fields"]
            for fieldset in items["plone.dublincore"]["fieldsets"]
        }
        self.assertEqual(fieldsets["default"], ["title", "description"])
        self.assertEqual(fieldsets["dates"], ["effective", "expires"])

    def test_behaviors_without_fields(self):
        self.assertEqual(self.items()["plone.locking"]["fieldsets"], [])

    def test_anonymous_and_members_are_denied(self):
        self.api.auth = None
        self.assertEqual(self.api.get("/@behaviors").status_code, 401)
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        transaction.commit()
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        self.assertEqual(self.api.get("/@behaviors").status_code, 401)
