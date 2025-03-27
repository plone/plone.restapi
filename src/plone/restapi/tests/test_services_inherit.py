from plone import api
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.behavior.registration import BehaviorRegistration
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.interfaces import IFolderish
from zope import schema
from zope.component import adapter
from zope.component import provideAdapter
from zope.component import provideUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface

import transaction
import unittest


class ITestBehavior(Interface):
    test_field = schema.TextLine(title="Test Field", required=False)


class ITestBehaviorMarker(Interface):
    pass


class ISecondBehavior(Interface):
    second_field = schema.TextLine(title="Second Field", required=False)


class ISecondBehaviorMarker(Interface):
    pass


class IValidatedBehavior(Interface):
    email = schema.TextLine(title="Email", required=True, constraint=lambda v: "@" in v)


class IValidatedBehaviorMarker(Interface):
    pass


@implementer(ITestBehavior)
@adapter(IFolderish)
class TestBehaviorAdapter:
    def __init__(self, context):
        self.context = context

    @property
    def test_field(self):
        return getattr(self.context, "test_field", None)

    @test_field.setter
    def test_field(self, value):
        setattr(self.context, "test_field", value)


@implementer(ISecondBehavior)
@adapter(IFolderish)
class SecondBehaviorAdapter:
    def __init__(self, context):
        self.context = context

    @property
    def second_field(self):
        return getattr(self.context, "second_field", None)

    @second_field.setter
    def second_field(self, value):
        setattr(self.context, "second_field", value)


@implementer(IValidatedBehavior)
@adapter(IFolderish)
class ValidatedBehaviorAdapter:
    def __init__(self, context):
        self.context = context

    @property
    def email(self):
        return getattr(self.context, "email", None)

    @email.setter
    def email(self, value):
        setattr(self.context, "email", value)


class TestServiceInherit(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        # Register primary test behavior
        self.register_behavior(
            ITestBehavior,
            ITestBehaviorMarker,
            TestBehaviorAdapter,
            "plone.testbehavior.ITestBehavior",
        )

        # Create main test content
        self.parent, self.child = self.create_folder_structure(
            "test_parent",
            "test_child",
            "Parent Folder",
            "Child Folder",
            ITestBehaviorMarker,
            parent_attrs={"test_field": "Inherited Value"},
        )

        transaction.commit()
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def register_behavior(self, interface, marker, adapter_class, name):
        """Helper to register a behavior."""
        registration = BehaviorRegistration(
            title=f"{interface.__name__} Registration",
            description="Test behavior",
            interface=interface,
            marker=marker,
            factory=adapter_class,
        )
        provideUtility(registration, name=name)
        provideAdapter(adapter_class)

    def create_folder_structure(
        self,
        parent_id,
        child_id,
        parent_title,
        child_title,
        marker_interface=None,
        parent_attrs=None,
        child_attrs=None,
    ):
        """Helper to create parent/child folders with optional attributes."""
        parent = api.content.create(
            container=self.portal,
            type="Folder",
            id=parent_id,
            title=parent_title,
            **(parent_attrs or {}),
        )
        child = api.content.create(
            container=parent,
            type="Folder",
            id=child_id,
            title=child_title,
            **(child_attrs or {}),
        )
        if marker_interface:
            alsoProvides(parent, marker_interface)
        return parent, child

    def tearDown(self):
        self.api_session.close()
        with api.env.adopt_roles(["Manager"]):
            api.content.delete(obj=self.parent)
        transaction.commit()

    def test_inherit_service_with_behavior_field(self):
        url = f"{self.child.absolute_url()}/@inherit?expand.inherit.behaviors=plone.testbehavior.ITestBehavior"
        response = self.api_session.get(url)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        behavior_data = data["plone.testbehavior.ITestBehavior"]

        self.assertEqual(behavior_data["data"]["test_field"], "Inherited Value")
        self.assertEqual(behavior_data["from"]["@id"], self.parent.absolute_url())

    def test_inherit_service_no_behavior_specified(self):
        response = self.api_session.get(f"{self.child.absolute_url()}/@inherit")
        self.assertEqual(response.json(), {})

    def test_inherit_service_invalid_behavior(self):
        url = f"{self.child.absolute_url()}/@inherit?expand.inherit.behaviors=invalid.behavior"
        response = self.api_session.get(url)
        self.assertNotIn("invalid.behavior", response.json())

    def test_inherit_multiple_behaviors(self):
        self.register_behavior(
            ISecondBehavior,
            ISecondBehaviorMarker,
            SecondBehaviorAdapter,
            "plone.testbehavior.ISecondBehavior",
        )

        self.parent.second_field = "Second Value"
        alsoProvides(self.parent, ISecondBehaviorMarker)
        transaction.commit()

        url = f"{self.child.absolute_url()}/@inherit?expand.inherit.behaviors=plone.testbehavior.ITestBehavior,plone.testbehavior.ISecondBehavior"
        response = self.api_session.get(url)
        data = response.json()

        self.assertIn("plone.testbehavior.ISecondBehavior", data)
        self.assertEqual(
            data["plone.testbehavior.ISecondBehavior"]["data"]["second_field"],
            "Second Value",
        )

    def test_inherit_schema_validation(self):
        self.register_behavior(
            IValidatedBehavior,
            IValidatedBehaviorMarker,
            ValidatedBehaviorAdapter,
            "plone.testbehavior.IValidatedBehavior",
        )

        validated_parent, validated_child = self.create_folder_structure(
            "valid_parent",
            "valid_child",
            "Valid Parent",
            "Valid Child",
            IValidatedBehaviorMarker,
            parent_attrs={"email": "test@example.com"},
        )
        transaction.commit()

        url = f"{validated_child.absolute_url()}/@inherit?expand.inherit.behaviors=plone.testbehavior.IValidatedBehavior"
        response = self.api_session.get(url)
        data = response.json()
        self.assertEqual(
            data["plone.testbehavior.IValidatedBehavior"]["data"]["email"],
            "test@example.com",
        )

    def test_inherit_depth(self):
        grandchild = api.content.create(
            container=self.child, type="Folder", id="grandchild"
        )
        transaction.commit()

        url = f"{grandchild.absolute_url()}/@inherit?expand.inherit.behaviors=plone.testbehavior.ITestBehavior"
        response = self.api_session.get(url)
        data = response.json()
        self.assertEqual(
            data["plone.testbehavior.ITestBehavior"]["from"]["title"], "Parent Folder"
        )

    def test_inherit_permissions(self):
        restricted_parent, restricted_child = self.create_folder_structure(
            "restricted",
            "restricted_child",
            "Restricted Parent",
            "Restricted Child",
            ITestBehaviorMarker,
            parent_attrs={"test_field": "Restricted Value"},
        )
        transaction.commit()

        logout()
        anon_session = RelativeSession(self.portal.absolute_url())
        anon_session.headers.update({"Accept": "application/json"})

        url = f"{restricted_child.absolute_url()}/@inherit?expand.inherit.behaviors=plone.testbehavior.ITestBehavior"
        response = anon_session.get(url)
        self.assertEqual(response.status_code, 401)

    def test_inherit_expansion(self):
        response = self.api_session.get(
            f"{self.child.absolute_url()}?expand=inherit&expand.inherit.behaviors=plone.testbehavior.ITestBehavior"
        )
        self.assertEqual(
            "Inherited Value",
            response.json()["@components"]["inherit"][
                "plone.testbehavior.ITestBehavior"
            ]["data"]["test_field"],
        )
