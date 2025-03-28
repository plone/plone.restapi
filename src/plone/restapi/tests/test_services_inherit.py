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


class TestServiceInherit(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        registration = BehaviorRegistration(
            title="ITestBehavior Registration",
            description="Test behavior",
            interface=ITestBehavior,
            marker=ITestBehaviorMarker,
            factory=TestBehaviorAdapter,
        )
        provideUtility(registration, name="plone.testbehavior.ITestBehavior")
        provideAdapter(TestBehaviorAdapter)

        # Create main test content
        self.parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="test_parent",
            title="Parent Folder",
            test_field="Inherited Value",
        )
        self.child = api.content.create(
            container=self.parent, type="Folder", id="test_child", title="Child Folder"
        )
        alsoProvides(self.parent, ITestBehaviorMarker)

        transaction.commit()
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

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
        registration = BehaviorRegistration(
            title="ISecondBehavior Registration",
            description="Test behavior",
            interface=ISecondBehavior,
            marker=ISecondBehaviorMarker,
            factory=SecondBehaviorAdapter,
        )
        provideUtility(registration, name="plone.testbehavior.ISecondBehavior")
        provideAdapter(SecondBehaviorAdapter)

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
        restricted_parent = api.content.create(
            container=self.portal,
            type="Folder",
            id="restricted",
            title="Restricted Parent",
            test_field="Restricted Value",
        )
        restricted_child = api.content.create(
            container=restricted_parent,
            type="Folder",
            id="restricted_child",
            title="Restricted Child",
        )
        alsoProvides(restricted_parent, ITestBehaviorMarker)
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
