from plone import api
from plone.restapi import testing
from plone.restapi.interfaces import ISerializeToJson
from zope.component import getMultiAdapter

import unittest


class TestSerializeUserToJsonAdapter(testing.PloneRestAPITestCase):
    """
    Test the user serializer used internally in the Rest API.
    """

    def setUp(self):
        """
        Create a user to test against.
        """
        super().setUp()

        properties = {
            "email": "noam.chomsky@example.com",
            "username": "noamchomsky",
            "fullname": "Noam Avram Chomsky",
            "home_page": "web.mit.edu/chomsky",
            "description": "Professor of Linguistics",
            "location": "Cambridge, MA",
        }
        self.user = api.user.create(
            email="noam.chomsky@example.com", username="noam", properties=properties
        )

    def serialize(self, user):
        serializer = getMultiAdapter((user, self.request), ISerializeToJson)
        return serializer()

    def test_serialize_returns_id(self):
        user = self.serialize(self.user)
        self.assertTrue(user)
        self.assertEqual("noam", user.get("id"))
        self.assertEqual("noam.chomsky@example.com", user.get("email"))
        self.assertEqual("Noam Avram Chomsky", user.get("fullname"))
        self.assertEqual("web.mit.edu/chomsky", user.get("home_page"))  # noqa
        self.assertEqual("Professor of Linguistics", user.get("description"))  # noqa
        self.assertEqual("Cambridge, MA", user.get("location"))

    def test_serialize_roles(self):
        user = self.serialize(self.user)
        self.assertIn("roles", user)
        self.assertNotIn("Authenticated", user["roles"])
        self.assertNotIn("Anonymous", user["roles"])

    def test_serialize_custom_member_schema(self):
        from plone.app.users.browser.schemaeditor import applySchema

        member_schema = """
            <model xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:form="http://namespaces.plone.org/supermodel/form"
                xmlns:users="http://namespaces.plone.org/supermodel/users"
                xmlns:i18n="http://xml.zope.org/namespaces/i18n"
                i18n:domain="plone">
              <schema name="member-fields">
                <field name="twitter" type="zope.schema.TextLine"
                         users:forms="In User Profile">
                  <description i18n:translate="help_twitter">
                    Twitter account
                  </description>
                  <required>False</required>
                  <title i18n:translate="label_twitter">Twitter Account</title>
                </field>
              </schema>
            </model>
        """
        applySchema(member_schema)
        user = api.user.create(
            email="donald.duck@example.com",
            username="donald",
            properties={"twitter": "TheRealDuck"},
        )
        res = self.serialize(user)
        self.assertIn("twitter", res)
        self.assertEqual(res["twitter"], "TheRealDuck")
