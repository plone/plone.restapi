# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.users.setuphandlers import import_schema
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.GenericSetup.tests.common import DummyImportContext

import transaction
import unittest

try:
    from Products.CMFPlone.factory import _IMREALLYPLONE5  # noqa
except ImportError:
    PLONE5 = False
else:
    PLONE5 = True


@unittest.skipIf(not PLONE5, "Just Plone 5 currently.")
class TestUserSchemaEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_userschema_get(self):
        response = self.api_session.get("/@userschema")

        self.assertEqual(200, response.status_code)
        response = response.json()

        self.assertIn("fullname", response["fieldsets"][0]["fields"])
        self.assertIn("email", response["fieldsets"][0]["fields"])
        self.assertIn("home_page", response["fieldsets"][0]["fields"])
        self.assertIn("description", response["fieldsets"][0]["fields"])
        self.assertIn("location", response["fieldsets"][0]["fields"])
        self.assertIn("portrait", response["fieldsets"][0]["fields"])

        self.assertIn("fullname", response["properties"])
        self.assertIn("email", response["properties"])
        self.assertIn("home_page", response["properties"])
        self.assertIn("description", response["properties"])
        self.assertIn("location", response["properties"])
        self.assertIn("portrait", response["properties"])

        self.assertIn("email", response["required"])

        self.assertTrue("object", response["type"])


@unittest.skipIf(not PLONE5, "Just Plone 5 currently.")
class TestCustomUserSchema(unittest.TestCase):
    """test userschema endpoint with a custom defined schema.
    we have taken the same example as in plone.app.users, thatç
    handles all kind of schema fields
    """

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        xml = """<model xmlns:lingua="http://namespaces.plone.org/supermodel/lingua" xmlns:users="http://namespaces.plone.org/supermodel/users" xmlns:form="http://namespaces.plone.org/supermodel/form" xmlns:i18n="http://xml.zope.org/namespaces/i18n" xmlns:security="http://namespaces.plone.org/supermodel/security" xmlns:marshal="http://namespaces.plone.org/supermodel/marshal" xmlns="http://namespaces.plone.org/supermodel/schema" i18n:domain="plone">
  <schema name="member-fields">
    <field name="home_page" type="zope.schema.URI" users:forms="In User Profile">
      <description i18n:translate="help_homepage">
          The URL for your external home page, if you have one.
      </description>
      <required>False</required>
      <title i18n:translate="label_homepage">Home Page</title>
    </field>
    <field name="description" type="zope.schema.Text" users:forms="In User Profile">
      <description i18n:translate="help_biography">
          A short overview of who you are and what you do. Will be displayed
          on your author page, linked from the items you create.
      </description>
      <required>False</required>
      <title i18n:translate="label_biography">Biography</title>
    </field>
    <field name="location" type="zope.schema.TextLine" users:forms="In User Profile">
      <description i18n:translate="help_location">
          Your location - either city and country - or in
          a company setting, where your office is located.
      </description>
      <required>False</required>
      <title i18n:translate="label_biography">Location</title>
    </field>
    <field name="portrait" type="plone.namedfile.field.NamedBlobImage" users:forms="In User Profile">
      <description i18n:translate="help_portrait">
          To add or change the portrait: click the "Browse" button; select a
          picture of yourself. Recommended image size is 75 pixels wide by
          100 pixels tall.
      </description>
      <required>False</required>
      <title i18n:translate="label_portrait">Portrait</title>
    </field>
    <field name="birthdate" type="zope.schema.Date" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Birthdate</title>
    </field>
    <field name="another_date" type="zope.schema.Datetime" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Another date</title>
    </field>
    <field name="age" type="zope.schema.Int" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Age</title>
    </field>
    <field name="department" type="zope.schema.Choice" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Department</title>
      <values>
        <element>Marketing</element>
        <element>Production</element>
        <element>HR</element>
      </values>
    </field>
    <field name="skills" type="zope.schema.Set" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Skills</title>
      <value_type type="zope.schema.Choice">
        <values>
          <element>Programming</element>
          <element>Management</element>
        </values>
      </value_type>
    </field>
    <field name="pi" type="zope.schema.Float" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Pi</title>
    </field>
    <field name="vegetarian" type="zope.schema.Bool" users:forms="In User Profile">
      <description/>
      <required>False</required>
      <title>Vegetarian</title>
    </field>
  </schema>
</model>
"""
        context = DummyImportContext(self.portal, purge=False)
        context._files = {"userschema.xml": xml}
        import_schema(context)
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_userschema_get(self):
        response = self.api_session.get("/@userschema")

        self.assertEqual(200, response.status_code)
        response = response.json()
        # Default fields
        self.assertIn("fullname", response["fieldsets"][0]["fields"])
        self.assertIn("email", response["fieldsets"][0]["fields"])
        self.assertIn("home_page", response["fieldsets"][0]["fields"])
        self.assertIn("description", response["fieldsets"][0]["fields"])
        self.assertIn("location", response["fieldsets"][0]["fields"])

        # added fields
        self.assertIn("portrait", response["fieldsets"][0]["fields"])
        self.assertIn("birthdate", response["fieldsets"][0]["fields"])
        self.assertIn("another_date", response["fieldsets"][0]["fields"])
        self.assertIn("age", response["fieldsets"][0]["fields"])
        self.assertIn("department", response["fieldsets"][0]["fields"])
        self.assertIn("skills", response["fieldsets"][0]["fields"])
        self.assertIn("pi", response["fieldsets"][0]["fields"])
        self.assertIn("vegetarian", response["fieldsets"][0]["fields"])
