from OFS.SimpleItem import SimpleItem
from plone.app.contentrules.actions import ActionAddForm
from plone.app.contentrules.actions import ActionEditForm
from plone.app.contentrules.browser.formhelper import ContentRuleFormWrapper
from plone.app.testing import FunctionalTesting
from plone.app.testing import PloneSandboxLayer
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.contentrules.rule.interfaces import IRuleElementData
from plone.restapi.testing import PLONE_RESTAPI_DX_FIXTURE
from plone.restapi.testing import RelativeSession
from plone.supermodel.directives import fieldset
from plone.supermodel.model import Schema
from plone.testing import zope
from zope import schema
from zope.configuration import xmlconfig
from zope.interface import implementer

import transaction
import unittest


class IFieldsetAction(Schema):
    """A rule action whose schema groups some fields into a fieldset."""

    base_value = schema.TextLine(title="Base value", required=True)

    fieldset(
        "advanced",
        label="Advanced",
        fields=["extra_title", "extra_description"],
    )

    extra_title = schema.TextLine(title="Extra title", default="hello")
    extra_description = schema.TextLine(title="Extra description", default="world")


@implementer(IFieldsetAction, IRuleElementData)
class FieldsetAction(SimpleItem):
    base_value = ""
    extra_title = "hello"
    extra_description = "world"

    element = "plone.restapi.tests.FieldsetAction"
    summary = "Fieldset action"


class FieldsetActionAddForm(ActionAddForm):
    schema = IFieldsetAction
    Type = FieldsetAction


class FieldsetActionAddFormView(ContentRuleFormWrapper):
    form = FieldsetActionAddForm


class FieldsetActionEditForm(ActionEditForm):
    schema = IFieldsetAction


class FieldsetActionEditFormView(ContentRuleFormWrapper):
    form = FieldsetActionEditForm


ZCML = """
<configure
    xmlns="http://namespaces.zope.org/zope"
    xmlns:browser="http://namespaces.zope.org/browser"
    xmlns:plone="http://namespaces.plone.org/plone"
    >
  <browser:page
      name="plone.restapi.tests.FieldsetAction"
      for="plone.app.contentrules.browser.interfaces.IRuleActionAdding"
      class="{module}.FieldsetActionAddFormView"
      permission="plone.app.contentrules.ManageContentRules"
      />
  <browser:page
      name="edit"
      for="{module}.IFieldsetAction"
      class="{module}.FieldsetActionEditFormView"
      permission="plone.app.contentrules.ManageContentRules"
      />
  <plone:ruleAction
      name="plone.restapi.tests.FieldsetAction"
      title="Fieldset action"
      description="Test action with a fieldset"
      for="*"
      event="*"
      schema="{module}.IFieldsetAction"
      factory="{module}.FieldsetAction"
      addview="plone.restapi.tests.FieldsetAction"
      editview="edit"
      />
</configure>
""".format(module=__name__)


class ContentRulesFieldsetLayer(PloneSandboxLayer):
    defaultBases = (PLONE_RESTAPI_DX_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        xmlconfig.string(ZCML, context=configurationContext)


CONTENT_RULES_FIELDSET_FIXTURE = ContentRulesFieldsetLayer()
CONTENT_RULES_FIELDSET_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(CONTENT_RULES_FIELDSET_FIXTURE, zope.WSGI_SERVER_FIXTURE),
    name="ContentRulesFieldsetLayer:Functional",
)


class TestContentRulesControlpanelFieldsets(unittest.TestCase):
    layer = CONTENT_RULES_FIELDSET_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        response = self.api_session.post(
            "/@controlpanels/content-rules",
            json={"title": "Fieldset rule", "event": "Comment added"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.rule_id = response.json()["id"]
        self.action_url = f"/@controlpanels/content-rules/{self.rule_id}/action"
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def add_action(self, **values):
        payload = {"type": "plone.restapi.tests.FieldsetAction", **values}
        response = self.api_session.post(self.action_url, json=payload)
        self.assertEqual(response.status_code, 201, response.text)
        transaction.commit()

    def get_action(self):
        response = self.api_session.get(f"{self.action_url}/0")
        self.assertEqual(response.status_code, 200, response.text)
        return response.json()

    def test_get_returns_values_for_every_schema_field(self):
        self.add_action(base_value="base")
        data = self.get_action()
        self.assertEqual(
            set(data["@schema"]["properties"]),
            {"base_value", "extra_title", "extra_description"},
        )
        self.assertEqual(data["base_value"], "base")
        self.assertEqual(data["extra_title"], "hello")
        self.assertEqual(data["extra_description"], "world")

    def test_add_sets_values_for_fields_in_fieldsets(self):
        self.add_action(
            base_value="base", extra_title="Title", extra_description="Description"
        )
        data = self.get_action()
        self.assertEqual(data["base_value"], "base")
        self.assertEqual(data["extra_title"], "Title")
        self.assertEqual(data["extra_description"], "Description")

    def test_update_sets_values_for_fields_in_fieldsets(self):
        self.add_action(base_value="base")
        response = self.api_session.patch(
            f"{self.action_url}/0",
            json={"base_value": "changed", "extra_title": "New title"},
        )
        self.assertEqual(response.status_code, 204, response.text)
        transaction.commit()
        data = self.get_action()
        self.assertEqual(data["base_value"], "changed")
        self.assertEqual(data["extra_title"], "New title")
        self.assertEqual(data["extra_description"], "world")
