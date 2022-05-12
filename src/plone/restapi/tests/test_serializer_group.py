from plone import api
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.component import getMultiAdapter

import unittest


class TestSerializeUserToJsonAdapters(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.gtool = api.portal.get_tool("portal_groups")
        properties = {
            "title": "Plone Team",
            "description": "We are Plone",
            "email": "ploneteam@plone.org",
        }
        self.gtool.addGroup(
            "ploneteam",
            (),
            (),
            properties=properties,
            title=properties["title"],
            description=properties["description"],
        )
        self.group = self.gtool.getGroupById("ploneteam")
        self.group.addMember(TEST_USER_ID)

    def serialize(self, user):
        serializer = getMultiAdapter((user, self.request), ISerializeToJson)
        return serializer()

    def serialize_summary(self, user):
        serializer = getMultiAdapter((user, self.request), ISerializeToJsonSummary)
        return serializer()

    def test_serialize_returns_id(self):
        group = self.serialize(self.group)
        self.assertTrue(group)
        self.assertEqual("ploneteam", group.get("id"))
        self.assertEqual("ploneteam@plone.org", group.get("email"))
        self.assertEqual("Plone Team", group.get("title"))
        self.assertEqual("We are Plone", group.get("description"))
        self.assertEqual(set(group["users"]), {"@id", "items_total", "items"})

    def test_summary(self):
        group = self.serialize_summary(self.group)
        self.assertTrue(group)
        self.assertEqual("ploneteam", group.get("id"))
        self.assertEqual("ploneteam@plone.org", group.get("email"))
        self.assertEqual("Plone Team", group.get("title"))
        self.assertEqual("We are Plone", group.get("description"))
        self.assertNotIn("users", group)
