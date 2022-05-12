from datetime import date
from datetime import datetime
from datetime import time
from datetime import timedelta
from DateTime import DateTime
from decimal import Decimal
from plone import api
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.textfield.interfaces import ITransformer
from plone.app.textfield.value import RichTextValue
from plone.namedfile.file import NamedFile
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.tests.test_expansion import ExpandableElementFoo
from plone.uuid.interfaces import IMutableUUID
from Products.CMFCore.utils import getToolByName
from zope.component import getGlobalSiteManager
from zope.component import getMultiAdapter
from zope.component import provideAdapter
from zope.component import queryUtility
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import json
import unittest


class AdapterCM:
    """Context manager that will temporarily register an adapter"""

    def __init__(self, adapter, from_, provides):
        self.adapter = adapter
        self.from_ = from_
        self.provides = provides
        self.gsm = getGlobalSiteManager()

    def __enter__(self):
        self.gsm.registerAdapter(self.adapter, self.from_, self.provides)

    def __exit__(self, exc_type, exc_value, traceback):
        self.gsm.unregisterAdapter(self.adapter, self.from_, self.provides)


class TestDXContentSerializer(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        richtext_value = RichTextValue("Käfer", "text/plain", "text/html")

        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc1",
            test_ascii_field="foo",
            test_asciiline_field="foo",
            test_bool_field=True,
            test_bytes_field="\xc3\xa4\xc3\xb6\xc3\xbc",
            test_bytesline_field="\xc3\xa4\xc3\xb6\xc3\xbc",
            test_choice_field="foo",
            test_date_field=date(2015, 7, 15),
            test_datetime_field=datetime(2015, 6, 20, 13, 22, 4),
            test_decimal_field=Decimal(1.1),
            test_dict_field={"foo": "bar", "spam": "eggs", "1": 1},
            test_float_field=1.5,
            test_frozenset_field=frozenset([1, 2, 3]),
            test_int_field=500,
            test_list_field=[1, "two", 3],
            test_set_field={"a", "b", "c"},
            test_text_field="Käfer",
            test_richtext_field=richtext_value,
            test_textline_field="Käfer",
            test_time_field=time(14, 15, 33),
            test_timedelta_field=timedelta(44),
            test_tuple_field=(1, 1),
            test_readonly_field="readonly",
            test_read_permission_field="Secret Stuff",
        )

        self.portal.doc1.creation_date = DateTime("2015-04-27T10:14:48+00:00")
        self.portal.doc1.modification_date = DateTime("2015-04-27T10:24:11+00:00")
        IMutableUUID(self.portal.doc1).set("30314724b77a4ec0abbad03d262837aa")

    def serialize(self, obj=None):
        if obj is None:
            obj = self.portal.doc1
        serializer = getMultiAdapter((obj, self.request), ISerializeToJson)
        return serializer()

    def test_serializer_returns_json_serializeable_object(self):
        obj = self.serialize()
        self.assertTrue(isinstance(json.dumps(obj), str), "Not JSON serializable")

    @unittest.skip("We do not include the context at this point")
    def test_serializer_includes_context(self):
        obj = self.serialize()
        self.assertIn("@context", obj)
        self.assertEqual("http://www.w3.org/ns/hydra/context.jsonld", obj["@context"])

    def test_serializer_includes_json_ld_id(self):
        obj = self.serialize()
        self.assertIn("@id", obj)
        self.assertEqual(self.portal.doc1.absolute_url(), obj["@id"])

    def test_serializer_includes_id(self):
        obj = self.serialize()
        self.assertIn("id", obj)
        self.assertEqual(self.portal.doc1.id, obj["id"])

    def test_serializer_includes_type(self):
        obj = self.serialize()
        self.assertIn("@type", obj)
        self.assertEqual(self.portal.doc1.portal_type, obj["@type"])

    def test_serializer_includes_review_state(self):
        obj = self.serialize()
        self.assertIn("review_state", obj)
        self.assertEqual("private", obj["review_state"])

    def test_serializer_includes_uid(self):
        obj = self.serialize()
        self.assertIn("UID", obj)
        self.assertEqual("30314724b77a4ec0abbad03d262837aa", obj["UID"])

    def test_serializer_includes_creation_date(self):
        obj = self.serialize()
        self.assertIn("created", obj)
        self.assertEqual("2015-04-27T10:14:48+00:00", obj["created"])

    def test_serializer_includes_modification_date(self):
        obj = self.serialize()
        self.assertIn("modified", obj)
        self.assertEqual("2015-04-27T10:24:11+00:00", obj["modified"])

    def test_serializer_ignores_field_without_read_permission(self):
        self.portal.doc1.test_read_permission_field = "Secret Stuff"
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        self.assertNotIn("test_read_permission_field", self.serialize())

    def test_serializer_includes_field_with_read_permission(self):
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        obj = self.serialize()
        self.assertIn("test_read_permission_field", obj)
        self.assertEqual("Secret Stuff", obj["test_read_permission_field"])

    def test_get_layout(self):
        current_layout = self.portal.doc1.getLayout()
        obj = self.serialize()
        self.assertIn("layout", obj)
        self.assertEqual(current_layout, obj["layout"])

    def test_serializer_includes_expansion(self):
        provideAdapter(
            ExpandableElementFoo,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name="foo",
        )
        obj = self.serialize()
        self.assertIn("foo", obj["@components"])
        self.assertEqual("collapsed", obj["@components"]["foo"])
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            ExpandableElementFoo,
            (Interface, IBrowserRequest),
            IExpandableElement,
            "foo",
        )

    def test_get_is_folderish(self):
        obj = self.serialize()
        self.assertIn("is_folderish", obj)
        self.assertEqual(False, obj["is_folderish"])

    def test_get_is_folderish_in_folder(self):
        self.portal.invokeFactory("Folder", id="folder")
        serializer = getMultiAdapter(
            (self.portal.folder, self.request), ISerializeToJson
        )
        obj = serializer()
        self.assertIn("is_folderish", obj)
        self.assertEqual(True, obj["is_folderish"])

    def test_nextprev_no_nextprev(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        doc = api.content.create(
            container=folder,
            type="Document",
            title="Item 1",
            description="One item alone in the folder",
        )
        data = self.serialize(doc)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual({}, data["next_item"])

    def test_nextprev_has_prev(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        api.content.create(
            container=folder,
            type="Document",
            title="Item 1",
            description="Previous item",
        )
        doc = api.content.create(
            container=folder,
            type="Document",
            title="Item 2",
            description="Current item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-1",
                "@type": "Document",
                "title": "Item 1",
                "description": "Previous item",
            },
            data["previous_item"],
        )
        self.assertEqual({}, data["next_item"])

    def test_nextprev_has_next(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        doc = api.content.create(
            container=folder,
            type="Document",
            title="Item 1",
            description="Current item",
        )
        api.content.create(
            container=folder, type="Document", title="Item 2", description="Next item"
        )
        data = self.serialize(doc)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-2",
                "@type": "Document",
                "title": "Item 2",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_has_nextprev(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        api.content.create(
            container=folder,
            type="Document",
            title="Item 1",
            description="Previous item",
        )
        doc = api.content.create(
            container=folder,
            type="Document",
            title="Item 2",
            description="Current item",
        )
        api.content.create(
            container=folder, type="Document", title="Item 3", description="Next item"
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-1",
                "@type": "Document",
                "title": "Item 1",
                "description": "Previous item",
            },
            data["previous_item"],
        )
        self.assertEqual(
            {
                "@id": "http://nohost/plone/folder-with-items/item-3",
                "@type": "Document",
                "title": "Item 3",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_root_no_nextprev(self):
        data = self.serialize()
        self.assertEqual({}, data["previous_item"])
        self.assertEqual({}, data["next_item"])

    def test_nextprev_root_has_prev(self):
        doc = api.content.create(
            container=self.portal,
            type="Document",
            title="Item 2",
            description="Current item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "title": "",
                "description": "",
            },
            data["previous_item"],
        )
        self.assertEqual({}, data["next_item"])

    def test_nextprev_root_has_next(self):
        api.content.create(
            container=self.portal,
            type="Document",
            title="Item 2",
            description="Next item",
        )
        data = self.serialize()
        self.assertEqual({}, data["previous_item"])
        self.assertEqual(
            {
                "@id": "http://nohost/plone/item-2",
                "@type": "Document",
                "title": "Item 2",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_root_has_nextprev(self):
        api.content.create(
            container=self.portal,
            type="Document",
            title="Item 1",
            description="Previous item",
        )
        doc = api.content.create(
            container=self.portal,
            type="Document",
            title="Item 2",
            description="Current item",
        )
        api.content.create(
            container=self.portal,
            type="Document",
            title="Item 3",
            description="Next item",
        )
        data = self.serialize(doc)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/item-1",
                "@type": "Document",
                "title": "Item 1",
                "description": "Previous item",
            },
            data["previous_item"],
        )
        self.assertEqual(
            {
                "@id": "http://nohost/plone/item-3",
                "@type": "Document",
                "title": "Item 3",
                "description": "Next item",
            },
            data["next_item"],
        )

    def test_nextprev_unordered_folder(self):
        folder = api.content.create(
            container=self.portal,
            type="Folder",
            title="Folder with items",
            description="This is a folder with some documents",
        )
        folder.setOrdering("unordered")
        doc = api.content.create(
            container=folder,
            type="Document",
            title="Item 1",
            description="One item alone in the folder",
        )
        data = self.serialize(doc)
        self.assertEqual({}, data["previous_item"])
        self.assertEqual({}, data["next_item"])

    def test_richtext_serializer_context(self):
        """This checks if the context is passed in correctly.

        We define a ITransformer, which returns the contexts portal_type.
        This is then verfied.
        """

        class RichtextTransform:
            """RichttextValue to show that the context is correctly passed
            in throughout the stack.
            """

            def __init__(self, context):
                self.context = context

            def __call__(self, value, mime_type):
                return self.context.portal_type

        with AdapterCM(RichtextTransform, (Interface,), ITransformer):
            obj = self.serialize()

        self.assertEqual(
            obj["test_richtext_field"]["data"], self.portal.doc1.portal_type
        )

    def test_allow_discussion_by_default(self):
        """Not globally addable, not fti enabled, not obj instance enabled"""
        self.portal.invokeFactory("Document", id="doc2")
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])

    def test_allow_discussion_obj_instance_allows_but_not_global_enabled(self):
        self.portal.invokeFactory("Document", id="doc2")
        self.portal.doc2.allow_discussion = True
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])

    def test_allow_discussion_fti_allows_not_global_enabled(self):
        self.portal.invokeFactory("Document", id="doc2")
        portal_types = getToolByName(self.portal, "portal_types")
        document_fti = getattr(portal_types, self.portal.doc2.portal_type)
        document_fti.allow_discussion = True
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])

    def test_allow_discussion_allows_global_enabled_but_nothing_else(self):
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])

    def test_allow_discussion_obj_instance_allows_global_enabled(self):
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        self.portal.doc2.allow_discussion = True
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(True, obj["allow_discussion"])

    def test_allow_discussion_obj_instance_not_set_global_enabled(self):
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])

    def test_allow_discussion_fti_allows_allows_global_enabled(self):
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        portal_types = getToolByName(self.portal, "portal_types")
        document_fti = getattr(portal_types, self.portal.doc2.portal_type)
        document_fti.allow_discussion = True
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(True, obj["allow_discussion"])

    def test_allow_discussion_fti_allows_allows_global_enabled_but_no_instance_allowed(
        self,
    ):  # noqa
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        portal_types = getToolByName(self.portal, "portal_types")
        document_fti = getattr(portal_types, self.portal.doc2.portal_type)
        document_fti.allow_discussion = True
        self.portal.doc2.allow_discussion = False

        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])

    def test_allow_discussion_fti_allows_allows_global_enabled_but_no_instance_set(
        self,
    ):  # noqa
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        portal_types = getToolByName(self.portal, "portal_types")
        document_fti = getattr(portal_types, self.portal.doc2.portal_type)
        document_fti.allow_discussion = True

        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(True, obj["allow_discussion"])

    def test_allow_discussion_fti_disallows_allows_global_enabled_but_instance_allowed(
        self,
    ):  # noqa
        self.portal.invokeFactory("Document", id="doc2")
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True
        portal_types = getToolByName(self.portal, "portal_types")
        document_fti = getattr(portal_types, self.portal.doc2.portal_type)
        document_fti.allow_discussion = False
        self.portal.doc2.allow_discussion = True

        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        obj = serializer()

        self.assertIn("allow_discussion", obj)
        self.assertEqual(True, obj["allow_discussion"])

    def test_allow_discussion_global_enabled_but_instance_has_no_discussion_behavior(
        self,
    ):  # noqa
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        settings.globally_enabled = True

        obj = self.serialize()
        self.assertIn("allow_discussion", obj)
        self.assertEqual(False, obj["allow_discussion"])


class TestDXContentPrimaryFieldTargetUrl(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc1",
            test_primary_namedfile_field=NamedFile(
                data="Spam and eggs", contentType="text/plain", filename="test.txt"
            ),
        )

        self.portal.invokeFactory(
            "DXTestDocument",
            id="doc2",
            test_primary_namedfile_field=None,
        )

        self.portal.doc1.creation_date = DateTime("2015-04-27T10:14:48+00:00")
        self.portal.doc1.modification_date = DateTime("2015-04-27T10:24:11+00:00")
        IMutableUUID(self.portal.doc1).set("30314724b77a4ec0abbad03d262837aa")

    def serialize(self):
        serializer = getMultiAdapter((self.portal.doc1, self.request), ISerializeToJson)
        return serializer()

    def test_primary_field_target(self):
        logout()
        serializer = getMultiAdapter((self.portal.doc1, self.request), ISerializeToJson)
        data = serializer()
        self.assertIn("targetUrl", data)
        download_url = "/".join(
            [
                self.portal.doc1.absolute_url(),
                "@@download/test_primary_namedfile_field",
            ]
        )
        self.assertEqual(data["targetUrl"], download_url)

    def test_primary_field_target_without_file(self):
        logout()
        serializer = getMultiAdapter((self.portal.doc2, self.request), ISerializeToJson)
        data = serializer()
        self.assertNotIn("targetUrl", data)

    def test_primary_field_target_with_edit_permissions(self):
        serializer = getMultiAdapter((self.portal.doc1, self.request), ISerializeToJson)
        data = serializer()
        self.assertNotIn("targetUrl", data)
