from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.autoform import directives
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.types.adapters import TextLineJsonSchemaProvider
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.typesettings.interfaces import ITypeSettings
from plone.restapi.typesettings.settings import TypeSettings
from zope import schema
from zope.component import getGlobalSiteManager
from zope.component import queryUtility
from zope.component.interfaces import IFactory
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import invariant
from zope.interface.exceptions import Invalid
from zope.schema.interfaces import ITextLine
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary

import ast
import transaction
import unittest


class ISponsorSettings(Interface):
    sponsors_enabled = schema.Bool(title="Enable sponsors")


class SponsorSettings(TypeSettings):
    """Example add-on settings, stored on the FTI and in a site attribute."""

    title = "Sponsors"
    order = 100
    schema = ISponsorSettings

    def read(self):
        return {"sponsors_enabled": getattr(self.context, "sponsors_enabled", False)}

    def write(self, data):
        if "sponsors_enabled" in data:
            self.context.sponsors_enabled = data["sponsors_enabled"]

    def remove(self):
        removed = getattr(self.context.aq_parent, "removed_sponsors", ())
        self.context.aq_parent.removed_sponsors = removed + (self.context.getId(),)


def errors(response):
    """Return the field errors of a 400 response.

    Like other services, the message holds the representation of the list.
    """
    return ast.literal_eval(response.json()["message"])


def tokens(value):
    """Return the tokens of serialized choice values."""
    if isinstance(value, list):
        return [tokens(item) for item in value]
    return value["token"]


class ContentTypesTestCase(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.api = RelativeSession(self.portal.absolute_url(), test=self)
        self.api.headers["Accept"] = "application/json"
        self.api.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def get(self, type_id="Document"):
        return self.api.get("/@content-types/" + type_id)

    def data(self, type_id="Document"):
        return self.get(type_id).json()["data"]

    def create(self, **data):
        return self.api.post("/@content-types", json={"title": "Custom type", **data})

    def patch(self, data, type_id="Document"):
        return self.api.patch("/@content-types/" + type_id, json=data)

    def register(self, factory, name, provided=ITypeSettings, required=None):
        gsm = getGlobalSiteManager()
        gsm.registerAdapter(factory, required, provided, name)
        self.addCleanup(gsm.unregisterAdapter, factory, required, provided, name)


class TestContentTypesRead(ContentTypesTestCase):
    def test_listing_has_every_type_with_its_settings(self):
        response = self.api.get("/@content-types")
        self.assertEqual(response.status_code, 200, response.text)
        result = response.json()
        self.assertEqual(result["items_total"], len(result["items"]))
        self.assertEqual(
            {item["id"] for item in result["items"]},
            set(self.portal.portal_types.objectIds()),
        )
        document = next(item for item in result["items"] if item["id"] == "Document")
        self.assertEqual(document, self.get().json())

    def test_item_representation(self):
        result = self.get().json()
        self.assertEqual(
            result["@id"], self.portal.absolute_url() + "/@content-types/Document"
        )
        self.assertEqual(result["title"], "Page")
        self.assertEqual(result["items_total"], 0)
        self.assertEqual(
            [fieldset["id"] for fieldset in result["schema"]["fieldsets"]],
            [
                "general",
                "contents",
                "visibility",
                "comments",
                "behaviors",
                "versioning",
            ],
        )
        fields = [
            name
            for fieldset in result["schema"]["fieldsets"]
            for name in fieldset["fields"]
        ]
        self.assertEqual(fields[:2], ["title", "description"])
        self.assertEqual(set(fields), set(result["schema"]["properties"]))
        self.assertEqual(set(result["data"]), set(fields))
        self.assertEqual(
            result["workflow"],
            {"id": "simple_publication_workflow", "follows_default": True},
        )

    def test_choices_use_tokens_and_titles(self):
        data = self.data("Folder")
        self.assertEqual(data["versioning"], {"token": "off", "title": "Off"})
        self.assertEqual(
            data["allowed_content_types_mode"], {"token": "all", "title": "All types"}
        )
        self.assertEqual(data["allowed_content_types"], [])

    def test_item_counts_include_private_items(self):
        response = self.api.post(
            "/", json={"@type": "Document", "id": "private", "title": "Private"}
        )
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(self.get().json()["items_total"], 1)

    def test_unknown_types_and_paths(self):
        for method in (self.api.get, self.api.patch, self.api.delete):
            for path in ("/@content-types/missing", "/@content-types/Document/extra"):
                self.assertEqual(method(path).status_code, 404, path)
        self.assertEqual(self.api.delete("/@content-types").status_code, 404)
        self.assertEqual(self.api.post("/@content-types/Document").status_code, 400)


class TestContentTypesUpdate(ContentTypesTestCase):
    def test_partial_update(self):
        before = self.data()
        response = self.patch(
            {
                "title": "Edited",
                "global_allow": False,
                "searchable": False,
                "default_page": False,
                "allow_discussion": True,
            }
        )
        self.assertEqual(response.status_code, 204, response.text)
        after = self.data()
        self.assertEqual(after["title"], "Edited")
        self.assertFalse(after["global_allow"])
        self.assertFalse(after["searchable"])
        self.assertFalse(after["default_page"])
        self.assertTrue(after["allow_discussion"])
        self.assertEqual(after["description"], before["description"])
        transaction.begin()
        self.assertEqual(self.portal.portal_types.Document.title, "Edited")
        self.assertIn(
            "Document", self.portal.portal_registry["plone.types_not_searched"]
        )

    def allowed(self, mode, types, type_id="Folder"):
        return self.patch(
            {"allowed_content_types_mode": mode, "allowed_content_types": types},
            type_id,
        )

    def test_allowed_content_types_modes(self):
        for mode, types in (
            ("selected", ["Image", "File"]),
            ("all", ["Image", "File"]),
            ("none", []),
            ("all", []),
        ):
            response = self.allowed(mode, types)
            self.assertEqual(response.status_code, 204, response.text)
            data = self.data("Folder")
            self.assertEqual(tokens(data["allowed_content_types_mode"]), mode)
            self.assertEqual(tokens(data["allowed_content_types"]), types)

    def test_all_keeps_the_selection(self):
        self.assertEqual(self.allowed("selected", ["Image"]).status_code, 204)
        response = self.patch({"allowed_content_types_mode": "all"}, "Folder")
        self.assertEqual(response.status_code, 204, response.text)
        transaction.begin()
        folder = self.portal.portal_types.Folder
        self.assertFalse(folder.filter_content_types)
        self.assertEqual(folder.allowed_content_types, ("Image",))
        response = self.patch({"allowed_content_types_mode": "selected"}, "Folder")
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(
            tokens(self.data("Folder")["allowed_content_types"]), ["Image"]
        )

    def test_partial_updates_are_checked_against_current_values(self):
        self.assertEqual(self.allowed("selected", ["Image"]).status_code, 204)
        # "none" with the stored selection is invalid until it is cleared.
        response = self.patch({"allowed_content_types_mode": "none"}, "Folder")
        self.assertEqual(response.status_code, 400, response.text)
        response = self.patch({"allowed_content_types": []}, "Folder")
        self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual(self.allowed("none", []).status_code, 204)

    def test_choice_values_accept_term_objects(self):
        response = self.patch(
            {
                "allowed_content_types_mode": {"token": "selected"},
                "allowed_content_types": [{"token": "Image", "title": "Image"}],
                "versioning": {"token": "manual"},
            },
            "Folder",
        )
        self.assertEqual(response.status_code, 204, response.text)
        data = self.data("Folder")
        self.assertEqual(tokens(data["allowed_content_types"]), ["Image"])
        self.assertEqual(tokens(data["versioning"]), "manual")

    def test_invalid_updates_change_nothing(self):
        before = self.data()
        invariant = None
        for invalid, field in (
            ({"global_allow": "yes"}, "global_allow"),
            ({"versioning": "sometimes"}, "versioning"),
            ({"unknown": True}, "unknown"),
            ({"title": ""}, "title"),
            ({"title": None}, "title"),
            ({"allowed_content_types_mode": "some"}, "allowed_content_types_mode"),
            ({"allowed_content_types": ["Image", "Image"]}, "allowed_content_types"),
            (
                {
                    "allowed_content_types_mode": "selected",
                    "allowed_content_types": ["missing"],
                },
                "allowed_content_types",
            ),
            (
                {
                    "allowed_content_types_mode": "selected",
                    "allowed_content_types": [],
                },
                invariant,
            ),
            (
                {
                    "allowed_content_types_mode": "none",
                    "allowed_content_types": ["Image"],
                },
                invariant,
            ),
        ):
            response = self.patch({"searchable": False, **invalid})
            self.assertEqual(response.status_code, 400, invalid)
            fields = [error.get("field") for error in errors(response)]
            self.assertIn(field, fields, invalid)
            self.assertEqual(self.data(), before)

    def test_body_must_be_an_object(self):
        for body in ([], "text"):
            response = self.patch(body)
            self.assertEqual(response.status_code, 400, response.text)

    def test_versioning_policies_and_behaviors(self):
        repository = self.portal.portal_repository
        for mode in ("off", "manual", "automatic", "off"):
            response = self.patch({"versioning": mode})
            self.assertEqual(response.status_code, 204, response.text)
            self.assertEqual(tokens(self.data()["versioning"]), mode)
            transaction.begin()
            policies = repository.getPolicyMap().get("Document", ())
            self.assertEqual("at_edit_autoversion" in policies, mode == "automatic")
            self.assertEqual(
                "Document" in repository.getVersionableContentTypes(), mode != "off"
            )
            behaviors = self.portal.portal_types.Document.behaviors
            self.assertEqual("plone.versioning" in behaviors, mode != "off")

    def test_versioning_updates_the_type_schema(self):
        self.assertEqual(self.patch({"versioning": "off"}).status_code, 204)
        properties = self.api.get("/@types/Document").json()["properties"]
        self.assertNotIn("changeNote", properties)
        self.assertEqual(self.patch({"versioning": "manual"}).status_code, 204)
        properties = self.api.get("/@types/Document").json()["properties"]
        self.assertIn("changeNote", properties)

    def test_versioning_keeps_custom_policies(self):
        repository = self.portal.portal_repository
        repository.addPolicy("custom_policy", "Custom policy")
        repository.addPolicyForContentType("Document", "custom_policy")
        transaction.commit()
        for mode in ("automatic", "manual", "off"):
            self.assertEqual(self.patch({"versioning": mode}).status_code, 204)
            transaction.begin()
            self.assertIn("custom_policy", repository.getPolicyMap()["Document"])

    def test_versioning_keeps_legacy_behavior_names_and_order(self):
        fti = self.portal.portal_types.Document
        behaviors = tuple(
            b for b in fti.behaviors if b not in ("plone.versioning", "plone.locking")
        ) + (
            "plone.app.versioningbehavior.behaviors.IVersionable",
            "plone.app.lockingbehavior.behaviors.ILocking",
        )
        fti.behaviors = behaviors
        transaction.commit()
        self.assertEqual(self.patch({"versioning": "automatic"}).status_code, 204)
        transaction.begin()
        self.assertEqual(fti.behaviors, behaviors)
        self.assertEqual(self.patch({"versioning": "off"}).status_code, 204)
        transaction.begin()
        self.assertNotIn(
            "plone.app.versioningbehavior.behaviors.IVersionable", fti.behaviors
        )
        self.assertIn("plone.app.lockingbehavior.behaviors.ILocking", fti.behaviors)


class TestContentTypesBehaviors(ContentTypesTestCase):
    def behaviors(self, type_id="Document"):
        return tokens(self.data(type_id)["behaviors"])

    def test_behaviors_are_the_ordered_list(self):
        fti = self.portal.portal_types.Document
        self.assertEqual(self.behaviors(), list(fti.behaviors))
        field = self.get().json()["schema"]["properties"]["behaviors"]
        self.assertEqual(field["type"], "array")
        self.assertTrue(field["uniqueItems"])
        choices = dict(field["items"]["choices"])
        self.assertEqual(choices["plone.leadimage"], "Lead Image")

    def test_patch_replaces_the_list_in_order(self):
        behaviors = ["plone.leadimage", "plone.dublincore", "plone.namefromtitle"]
        response = self.patch({"behaviors": behaviors})
        self.assertEqual(response.status_code, 204, response.text)
        transaction.begin()
        self.assertEqual(self.portal.portal_types.Document.behaviors, tuple(behaviors))
        self.assertEqual(self.behaviors(), behaviors)
        # The schema follows.
        properties = self.api.get("/@types/Document").json()["properties"]
        self.assertIn("image", properties)
        self.assertNotIn("relatedItems", properties)

    def test_legacy_names_are_listed_by_name(self):
        fti = self.portal.portal_types.Document
        fti.behaviors = ("plone.app.dexterity.behaviors.metadata.IDublinCore",)
        transaction.commit()
        self.assertEqual(self.behaviors(), ["plone.dublincore"])

    def test_unregistered_behaviors_are_kept_but_not_listed(self):
        fti = self.portal.portal_types.Document
        fti.behaviors = ("plone.dublincore", "collective.gone")
        transaction.commit()
        self.assertEqual(self.behaviors(), ["plone.dublincore"])
        self.assertEqual(self.patch({"behaviors": ["plone.basic"]}).status_code, 204)
        transaction.begin()
        self.assertEqual(fti.behaviors, ("plone.basic", "collective.gone"))

    def test_unknown_and_repeated_behaviors_are_refused(self):
        before = self.portal.portal_types.Document.behaviors
        response = self.patch({"behaviors": ["plone.dublincore", "collective.nope"]})
        self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual([e["field"] for e in errors(response)], ["behaviors"])
        response = self.patch({"behaviors": ["plone.basic", "plone.basic"]})
        self.assertEqual(response.status_code, 400, response.text)
        transaction.begin()
        self.assertEqual(self.portal.portal_types.Document.behaviors, before)

    def test_versioning_decides_about_its_behavior(self):
        behaviors = [b for b in self.behaviors() if b != "plone.versioning"]
        response = self.patch({"behaviors": behaviors, "versioning": "manual"})
        self.assertEqual(response.status_code, 204, response.text)
        self.assertIn("plone.versioning", self.behaviors())
        response = self.patch(
            {"behaviors": behaviors + ["plone.versioning"], "versioning": "off"}
        )
        self.assertEqual(response.status_code, 204, response.text)
        self.assertNotIn("plone.versioning", self.behaviors())

    def test_only_dexterity_types_have_behaviors(self):
        data = self.data("Discussion Item")
        self.assertNotIn("behaviors", data)


class TestContentTypesCreate(ContentTypesTestCase):
    def test_create_with_defaults(self):
        response = self.create(description="Talks and workshops")
        self.assertEqual(response.status_code, 201, response.text)
        result = response.json()
        self.assertEqual(result["id"], "custom_type")
        self.assertEqual(response.headers["Location"], result["@id"])
        self.assertEqual(result["data"]["description"], "Talks and workshops")
        self.assertEqual(tokens(result["data"]["allowed_content_types_mode"]), "none")
        transaction.begin()
        fti = self.portal.portal_types.custom_type
        self.assertEqual(fti.factory, "custom_type")
        self.assertEqual(fti.klass, "plone.dexterity.content.Container")
        self.assertEqual(fti.behaviors, ("plone.dublincore", "plone.namefromtitle"))
        response = self.api.post("/", json={"@type": "custom_type", "title": "An item"})
        self.assertEqual(response.status_code, 201, response.text)

    def test_ids_with_spaces_have_encoded_urls(self):
        response = self.create(id="Custom Type")
        self.assertEqual(response.status_code, 201, response.text)
        self.assertTrue(response.headers["Location"].endswith("/Custom%20Type"))
        self.assertEqual(self.get("Custom%20Type").json()["id"], "Custom Type")

    def test_invalid_creation(self):
        self.assertEqual(self.create(id="Document").status_code, 409)
        for data in (
            {"title": ""},
            {"title": 12},
            {"id": ""},
            {"id": "bad/id"},
            {"id": "@@bad"},
            {"id": "_bad"},
            {"id": "aq_parent"},
            {"copy_from": ""},
            {"copy_from": "missing"},
            {"unexpected": 1},
        ):
            response = self.create(**data)
            self.assertEqual(response.status_code, 400, (data, response.text))
        response = self.api.post("/@content-types", json={})
        self.assertEqual(response.status_code, 400, response.text)
        for body in ([], "text"):
            response = self.api.post("/@content-types", json=body)
            self.assertEqual(response.status_code, 400, response.text)

    def test_copy_schema_behaviors_settings_and_workflow(self):
        response = self.api.post(
            "/@types/Document",
            json={"factory": "Text line (String)", "title": "Custom field"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        response = self.patch(
            {
                "searchable": False,
                "default_page": True,
                "allow_discussion": True,
                "versioning": "automatic",
            }
        )
        self.assertEqual(response.status_code, 204, response.text)
        transaction.begin()
        self.portal.portal_workflow.setChainForPortalTypes(
            ("Document",), ("one_state_workflow",)
        )
        transaction.commit()
        source = self.get().json()
        response = self.create(
            id="Copy", title="Copy", description="Copied", copy_from="Document"
        )
        self.assertEqual(response.status_code, 201, response.text)
        result = response.json()
        self.assertEqual(
            result["data"],
            {**source["data"], "title": "Copy", "description": "Copied"},
        )
        self.assertEqual(
            result["workflow"], {"id": "one_state_workflow", "follows_default": False}
        )
        transaction.begin()
        types = self.portal.portal_types
        self.assertEqual(types.Copy.behaviors, types.Document.behaviors)
        self.assertEqual(types.Copy.factory, "Copy")
        self.assertEqual(types.Copy.add_view_expr, "string:${folder_url}/++add++Copy")
        self.assertIsNotNone(queryUtility(IFactory, name="Copy", context=self.portal))
        self.assertEqual(
            [a.getId() for a in types.Copy.listActions()],
            [a.getId() for a in types.Document.listActions()],
        )
        self.assertIn("custom_field", self.api.get("/@types/Copy").json()["properties"])
        # The copy is independent of the source.
        response = self.api.delete("/@types/Copy/custom_field")
        self.assertEqual(response.status_code, 204, response.text)
        self.assertIn(
            "custom_field", self.api.get("/@types/Document").json()["properties"]
        )
        self.assertEqual(self.patch({"title": "Independent"}, "Copy").status_code, 204)
        self.assertEqual(self.get().json()["title"], source["title"])

    def test_copy_keeps_description_when_not_given(self):
        response = self.create(id="Copy", copy_from="Document")
        self.assertEqual(response.status_code, 201, response.text)
        self.assertEqual(
            response.json()["data"]["description"], self.data()["description"]
        )

    def test_copy_keeps_custom_policies_and_workflow_overrides(self):
        repository = self.portal.portal_repository
        repository.addPolicy("custom_policy", "Custom policy")
        repository.addPolicyForContentType("Document", "custom_policy")
        workflow = self.portal.portal_workflow
        for index, chain in enumerate((None, (), ("simple_publication_workflow",))):
            workflow.setChainForPortalTypes(("Document",), chain)
            transaction.commit()
            source = self.get().json()
            self.assertEqual(source["workflow"]["follows_default"], chain is None)
            response = self.create(id=f"Copy{index}", copy_from="Document")
            self.assertEqual(response.status_code, 201, response.text)
            self.assertEqual(response.json()["workflow"], source["workflow"])
            transaction.begin()
            self.assertEqual(
                set(repository.getPolicyMap()["Document"]),
                set(repository.getPolicyMap()[f"Copy{index}"]),
            )


class TestContentTypesDelete(ContentTypesTestCase):
    def test_delete(self):
        self.assertEqual(self.create().status_code, 201)
        response = self.api.delete("/@content-types/custom_type")
        self.assertEqual(response.status_code, 204, response.text)
        self.assertEqual(self.get("custom_type").status_code, 404)

    def test_delete_refused_while_items_exist(self):
        response = self.api.post(
            "/", json={"@type": "Document", "id": "private", "title": "Private"}
        )
        self.assertEqual(response.status_code, 201, response.text)
        response = self.api.delete("/@content-types/Document")
        self.assertEqual(response.status_code, 409, response.text)
        self.assertEqual(response.json()["items_total"], 1)
        self.assertEqual(self.get().status_code, 200)

    def test_only_dexterity_types_can_be_deleted(self):
        response = self.api.delete("/@content-types/Plone%20Site")
        self.assertEqual(response.status_code, 400, response.text)
        cmf_types = [
            fti.getId()
            for fti in self.portal.portal_types.listTypeInfo()
            if fti.meta_type != "Dexterity FTI"
        ]
        for type_id in cmf_types:
            response = self.api.delete(f"/@content-types/{type_id}")
            self.assertEqual(response.status_code, 400, response.text)

    def test_delete_cleans_up_so_a_new_type_starts_clean(self):
        self.assertEqual(self.create(id="Temporary").status_code, 201)
        response = self.patch(
            {"searchable": False, "default_page": True, "versioning": "automatic"},
            "Temporary",
        )
        self.assertEqual(response.status_code, 204, response.text)
        response = self.patch(
            {
                "allowed_content_types_mode": "selected",
                "allowed_content_types": ["Document", "Temporary"],
            },
            "Folder",
        )
        self.assertEqual(response.status_code, 204, response.text)
        transaction.begin()
        repository = self.portal.portal_repository
        repository.addPolicy("custom_policy", "Custom policy")
        repository.addPolicyForContentType("Temporary", "custom_policy")
        self.portal.portal_workflow.setChainForPortalTypes(
            ("Temporary",), ("one_state_workflow",)
        )
        transaction.commit()

        self.assertEqual(self.api.delete("/@content-types/Temporary").status_code, 204)
        self.assertEqual(self.create(id="Temporary").status_code, 201)
        result = self.get("Temporary").json()
        self.assertTrue(result["data"]["searchable"])
        self.assertFalse(result["data"]["default_page"])
        self.assertEqual(tokens(result["data"]["versioning"]), "off")
        self.assertTrue(result["workflow"]["follows_default"])
        self.assertEqual(
            tokens(self.data("Folder")["allowed_content_types"]),
            ["Document"],
        )
        transaction.begin()
        self.assertFalse(repository.getPolicyMap().get("Temporary"))


class TestContentTypesAddOns(ContentTypesTestCase):
    def test_addon_fieldset(self):
        self.register(SponsorSettings, "collective.sponsors")
        result = self.get().json()
        fieldset = result["schema"]["fieldsets"][-1]
        self.assertEqual(fieldset["id"], "collective.sponsors")
        self.assertEqual(fieldset["title"], "Sponsors")
        self.assertEqual(fieldset["fields"], ["sponsors_enabled"])
        self.assertFalse(result["data"]["sponsors_enabled"])
        self.assertEqual(self.patch({"sponsors_enabled": "yes"}).status_code, 400)
        self.assertEqual(self.patch({"sponsors_enabled": True}).status_code, 204)
        self.assertTrue(self.data()["sponsors_enabled"])

    def test_addon_settings_are_copied_and_removed(self):
        self.register(SponsorSettings, "collective.sponsors")
        self.assertEqual(self.patch({"sponsors_enabled": True}).status_code, 204)
        response = self.create(id="Sponsored", copy_from="Document")
        self.assertEqual(response.status_code, 201, response.text)
        self.assertTrue(response.json()["data"]["sponsors_enabled"])
        self.assertEqual(self.api.delete("/@content-types/Sponsored").status_code, 204)
        transaction.begin()
        self.assertEqual(self.portal.portal_types.removed_sponsors, ("Sponsored",))

    def test_addon_validation_prevents_all_writes(self):
        class RestrictedSponsors(SponsorSettings):
            def validate(self, data):
                if data.get("sponsors_enabled"):
                    return [{"field": "sponsors_enabled", "message": "Not available"}]
                return []

        self.register(RestrictedSponsors, "sponsors")
        before = self.data()
        response = self.patch({"title": "Must not persist", "sponsors_enabled": True})
        self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual(
            errors(response),
            [
                {
                    "field": "sponsors_enabled",
                    "message": "Not available",
                    "error": "ValidationError",
                }
            ],
        )
        self.assertEqual(self.data(), before)

    def test_addon_permission(self):
        class ManagerSponsors(SponsorSettings):
            permission = "cmf.ManagePortal"

        self.register(ManagerSponsors, "sponsors")
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        transaction.commit()
        self.assertIn("sponsors_enabled", self.data())
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        result = self.get().json()
        self.assertNotIn("sponsors_enabled", result["data"])
        self.assertNotIn("sponsors_enabled", result["schema"]["properties"])
        self.assertEqual(self.patch({"sponsors_enabled": True}).status_code, 400)
        self.assertEqual(self.patch({"title": "Edited"}).status_code, 204)

    def test_readonly_omitted_display_and_order_directives(self):
        class IFormSettings(Interface):
            editable = schema.TextLine(title="Editable")
            internal = schema.TextLine(title="Internal")
            summary = schema.TextLine(title="Summary")
            computed = schema.TextLine(title="Computed", readonly=True)
            directives.omitted("internal")
            directives.mode(summary="display")
            directives.order_before(summary="editable")

        class FormSettings(TypeSettings):
            schema = IFormSettings

            def read(self):
                return {
                    name: getattr(self.context, name, name)
                    for name in ("editable", "internal", "summary", "computed")
                }

            def write(self, data):
                for name, value in data.items():
                    setattr(self.context, name, value)

        self.register(FormSettings, "form")
        result = self.get().json()
        properties = result["schema"]["properties"]
        for name in ("internal", "computed"):
            self.assertNotIn(name, properties)
            self.assertNotIn(name, result["data"])
        self.assertTrue(properties["summary"]["readOnly"])
        self.assertEqual(properties["summary"]["mode"], "display")
        self.assertNotIn("summary", result["schema"]["required"])
        self.assertEqual(
            result["schema"]["fieldsets"][-1]["fields"], ["summary", "editable"]
        )
        for name in ("internal", "summary", "computed"):
            self.assertEqual(self.patch({name: "Changed"}).status_code, 400, name)
        self.assertEqual(self.patch({"editable": "Changed"}).status_code, 204)
        self.assertEqual(self.data()["editable"], "Changed")

    def test_nullable_field(self):
        class INullable(Interface):
            sponsors_enabled = schema.Bool(title="Enable sponsors", required=False)

        class NullableSponsors(SponsorSettings):
            schema = INullable

        self.register(NullableSponsors, "sponsors")
        self.assertEqual(self.patch({"sponsors_enabled": None}).status_code, 204)
        self.assertIsNone(self.data()["sponsors_enabled"])

    def test_field_conversion_and_constraints(self):
        class IExtraSettings(Interface):
            limit = schema.Int(title="Limit", min=1, max=10)
            level = schema.Choice(
                title="Level",
                vocabulary=SimpleVocabulary(
                    [SimpleTerm(1, "one", "One"), SimpleTerm(2, "two", "Two")]
                ),
            )
            starts = schema.Datetime(title="Starts", required=False)

        class ExtraSettings(TypeSettings):
            schema = IExtraSettings

            def read(self):
                return {
                    "limit": getattr(self.context, "limit", 1),
                    "level": getattr(self.context, "level", 1),
                    "starts": getattr(self.context, "starts", None),
                }

            def write(self, data):
                for name, value in data.items():
                    setattr(self.context, name, value)

        self.register(ExtraSettings, "extra")
        result = self.get().json()
        properties = result["schema"]["properties"]
        self.assertEqual(properties["limit"]["minimum"], 1)
        self.assertEqual(properties["level"]["enum"], ["one", "two"])
        self.assertIn("limit", result["schema"]["required"])
        self.assertNotIn("starts", result["schema"]["required"])
        self.assertEqual(result["data"]["level"], {"token": "one", "title": "One"})
        response = self.patch({"limit": 0, "title": "Must not persist"})
        self.assertEqual(response.status_code, 400, response.text)
        self.assertEqual(self.get().json()["title"], result["title"])
        response = self.patch(
            {"limit": 5, "level": "two", "starts": "2026-10-19T12:00:00+00:00"}
        )
        self.assertEqual(response.status_code, 204, response.text)
        data = self.data()
        self.assertEqual(data["level"], {"token": "two", "title": "Two"})
        self.assertEqual(data["starts"], "2026-10-19T12:00:00+00:00")
        transaction.begin()
        self.assertEqual(self.portal.portal_types.Document.level, 2)
        self.assertEqual(self.portal.portal_types.Document.starts.year, 2026)

    def test_invariants_see_current_values(self):
        class ILimits(Interface):
            lower = schema.Int(title="Lower")
            upper = schema.Int(title="Upper")

            @invariant
            def ordered(data):
                if data.lower > data.upper:
                    raise Invalid("Lower must not exceed upper")

        class LimitsSettings(TypeSettings):
            schema = ILimits

            def read(self):
                return {
                    "lower": getattr(self.context, "lower", 1),
                    "upper": getattr(self.context, "upper", 10),
                }

            def write(self, data):
                for name, value in data.items():
                    setattr(self.context, name, value)

        self.register(LimitsSettings, "limits")
        before = self.data()
        response = self.patch({"lower": 20, "title": "Must not persist"})
        self.assertEqual(response.status_code, 400, response.text)
        self.assertIn("Lower must not exceed upper", response.text)
        self.assertEqual(self.data(), before)
        self.assertEqual(self.patch({"upper": 30}).status_code, 204)
        self.assertEqual(self.patch({"lower": 20}).status_code, 204)
        self.assertEqual(self.data()["lower"], 20)

    def test_custom_field_adapters(self):
        class ICustomText(ITextLine):
            pass

        @implementer(ICustomText)
        class CustomText(schema.TextLine):
            pass

        class ICustomSettings(Interface):
            custom_setting = CustomText(title="Custom setting")

        class CustomSettings(TypeSettings):
            schema = ICustomSettings

            def read(self):
                return {
                    "custom_setting": getattr(self.context, "custom_setting", "initial")
                }

            def write(self, data):
                self.context.custom_setting = data["custom_setting"]

        class CustomSchemaProvider(TextLineJsonSchemaProvider):
            def additional(self):
                return {**super().additional(), "widget": "custom-widget"}

        class CustomSerializer(DefaultFieldSerializer):
            def __call__(self):
                return "wire:" + super().__call__()

        class CustomDeserializer(DefaultFieldDeserializer):
            def __call__(self, value):
                if not value.startswith("wire:"):
                    raise ValueError("Expected wire prefix")
                return super().__call__(value[5:])

        self.register(CustomSettings, "custom")
        required = (ICustomText, IDexterityContent, Interface)
        self.register(CustomSchemaProvider, "", IJsonSchemaProvider, required)
        self.register(CustomSerializer, "", IFieldSerializer, required)
        self.register(CustomDeserializer, "", IFieldDeserializer, required)
        result = self.get().json()
        self.assertEqual(
            result["schema"]["properties"]["custom_setting"]["widget"],
            "custom-widget",
        )
        self.assertEqual(result["data"]["custom_setting"], "wire:initial")
        self.assertEqual(self.patch({"custom_setting": "plain"}).status_code, 400)
        self.assertEqual(self.patch({"custom_setting": "wire:new"}).status_code, 204)
        self.assertEqual(self.data()["custom_setting"], "wire:new")
        transaction.begin()
        self.assertEqual(self.portal.portal_types.Document.custom_setting, "new")


class TestContentTypesPermissions(ContentTypesTestCase):
    REQUESTS = (
        ("get", "/@content-types"),
        ("get", "/@content-types/Document"),
        ("post", "/@content-types"),
        ("patch", "/@content-types/Document"),
        ("delete", "/@content-types/Document"),
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

    def test_site_administrator_is_allowed(self):
        setRoles(self.portal, TEST_USER_ID, ["Site Administrator"])
        transaction.commit()
        self.api.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        self.assertEqual(self.get().status_code, 200)
