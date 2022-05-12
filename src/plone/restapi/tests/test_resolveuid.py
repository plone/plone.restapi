from plone.app.testing import login
from plone.app.testing import logout
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedBlobImage
from plone.namedfile.file import NamedFile
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from unittest import TestCase
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter

import os
import requests
import transaction


class TestBlocksResolveUIDFunctional(TestCase):

    layer = PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.portal.invokeFactory("Folder", id="folder1", title="My Folder")
        self.portal.invokeFactory("Document", id="target", title="Link Target")
        wftool = getToolByName(self.portal, "portal_workflow")
        wftool.doActionFor(self.portal.folder1, "publish")
        transaction.commit()

    def test_create_document_with_link_stores_uuid(self):
        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
                "blocks": {
                    "09e39ddf-a945-49f2-b609-ea427ac3430b": {
                        "@type": "text",
                        "text": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [
                                        {"key": 0, "length": 4, "offset": 0}
                                    ],
                                    "inlineStyleRanges": [],
                                    "key": "ark35",
                                    "text": "Link",
                                    "type": "unstyled",
                                }
                            ],
                            "entityMap": {
                                "0": {
                                    "data": {"url": f"{self.portal_url}/target"},
                                    "mutability": "MUTABLE",
                                    "type": "LINK",
                                }
                            },
                        },
                    },
                    "21270e22-3a61-4780-b164-d6be56d942f4": {"@type": "title"},
                },
                "blocks_layout": {
                    "items": [
                        "21270e22-3a61-4780-b164-d6be56d942f4",
                        "09e39ddf-a945-49f2-b609-ea427ac3430b",
                    ]
                },
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()

        target_uuid = IUUID(self.portal.target)
        self.assertEqual(
            f"../../resolveuid/{target_uuid}",
            self.portal.folder1.mydocument.blocks.get(
                "09e39ddf-a945-49f2-b609-ea427ac3430b"
            )
            .get("text")
            .get("entityMap")
            .get("0")
            .get("data")
            .get("url"),
        )

    def test_create_document_with_image_block_stores_uuid(self):
        self.portal.invokeFactory("Image", id="image", title="Image")
        image_file = os.path.join(os.path.dirname(__file__), "image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.image.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename="image.png"
        )
        self.portal.image.image_caption = "This is an image caption."
        transaction.commit()

        target_uuid = IUUID(self.portal.image)

        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
                "blocks": {
                    "09e39ddf-a945-49f2-b609-ea427ac3430b": {
                        "@type": "image",
                        "url": f"{self.portal_url}/image",
                    },
                    "21270e22-3a61-4780-b164-d6be56d942f4": {"@type": "title"},
                },
                "blocks_layout": {
                    "items": [
                        "21270e22-3a61-4780-b164-d6be56d942f4",
                        "09e39ddf-a945-49f2-b609-ea427ac3430b",
                    ]
                },
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()

        self.assertEqual(
            f"../../resolveuid/{target_uuid}",
            self.portal.folder1.mydocument.blocks.get(
                "09e39ddf-a945-49f2-b609-ea427ac3430b"
            ).get("url"),
        )

    def test_create_document_with_image_block_and_href_stores_uuid(self):
        self.portal.invokeFactory("Document", id="linked_document", title="Linked Doc")
        self.portal.invokeFactory("Image", id="image", title="Image")
        image_file = os.path.join(os.path.dirname(__file__), "image.png")
        with open(image_file, "rb") as f:
            image_data = f.read()
        self.portal.image.image = NamedBlobImage(
            data=image_data, contentType="image/png", filename="image.png"
        )
        self.portal.image.image_caption = "This is an image caption."
        transaction.commit()

        target_uuid = IUUID(self.portal.image)
        liked_doc_uuid = IUUID(self.portal.linked_document)

        response = requests.post(
            self.portal.folder1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document",
                "blocks": {
                    "09e39ddf-a945-49f2-b609-ea427ac3430b": {
                        "@type": "image",
                        "url": f"{self.portal_url}/image",
                        "href": f"{self.portal_url}/linked_document",
                    },
                    "21270e22-3a61-4780-b164-d6be56d942f4": {"@type": "title"},
                },
                "blocks_layout": {
                    "items": [
                        "21270e22-3a61-4780-b164-d6be56d942f4",
                        "09e39ddf-a945-49f2-b609-ea427ac3430b",
                    ]
                },
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()

        self.assertEqual(
            f"../../resolveuid/{target_uuid}",
            self.portal.folder1.mydocument.blocks.get(
                "09e39ddf-a945-49f2-b609-ea427ac3430b"
            ).get("url"),
        )
        self.assertEqual(
            f"../../resolveuid/{liked_doc_uuid}",
            self.portal.folder1.mydocument.blocks.get(
                "09e39ddf-a945-49f2-b609-ea427ac3430b"
            ).get("href"),
        )


class TestBlocksResolveUID(TestCase):
    layer = PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
    maxDiff = None

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.doc1 = self.portal[
            self.portal.invokeFactory(
                "Document", id="doc1", title="Document with Blocks"
            )
        ]
        self.doc2 = self.portal[
            self.portal.invokeFactory("Document", id="doc2", title="Target Document")
        ]

        self.doc_primary_field_url = self.portal[
            self.portal.invokeFactory(
                "DXTestDocument",
                id="doc_primary_field_url",
                title="Target Document with primary file field",
                test_primary_namedfile_field=NamedFile(
                    data="Spam and eggs",
                    contentType="text/plain",
                    filename="test.txt",
                ),
            )
        ]

    def serialize(self, fieldname, value):
        for schema in iterSchemata(self.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        dm = getMultiAdapter((self.doc1, field), IDataManager)
        dm.set(value)
        serializer = getMultiAdapter((field, self.doc1, self.request), IFieldSerializer)
        return serializer()

    def deserialize(self, fieldname, value):
        for schema in iterSchemata(self.portal.doc1):
            if fieldname in schema:
                field = schema.get(fieldname)
                break
        deserializer = getMultiAdapter(
            (field, self.portal.doc1, self.request), IFieldDeserializer
        )
        return deserializer(value)

    def test_blocks_field_serialization_resolves_uids(self):
        uid = IUUID(self.doc2)
        blocks = {
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "Volto also supports other APIs.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc2.absolute_url(),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc2.absolute_url(),
        )

    def test_resolveuid_keeps_suffix(self):
        uid = IUUID(self.doc2)
        blocks = {
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "entityMap": {
                        "0": {
                            "data": {
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}/view",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    }
                },
            }
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc2.absolute_url() + "/view",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc2.absolute_url() + "/view",
        )

    def test_resolveuid_gets_serialized_for_standard_fields(self):
        uid = IUUID(self.doc2)
        blocks = {"aaa": {"@type": "foo", "url": f"../resolveuid/{uid}/view"}}
        value = self.serialize("blocks", blocks)
        self.assertEqual(value["aaa"]["url"], self.doc2.absolute_url() + "/view")

        blocks = {"aaa": {"@type": "foo", "href": f"../resolveuid/{uid}/view"}}
        value = self.serialize("blocks", blocks)
        self.assertEqual(value["aaa"]["href"], self.doc2.absolute_url() + "/view")

    def test_resolveuid_serialize_take_care_of_primary_fields(self):
        logout()
        uid = IUUID(self.doc_primary_field_url)
        blocks = {"aaa": {"@type": "foo", "url": f"../resolveuid/{uid}"}}
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["aaa"]["url"],
            self.doc_primary_field_url.absolute_url()
            + "/@@download/test_primary_namedfile_field",
        )

    def test_keeps_resolveuid_link_if_unknown_uid(self):
        uid = "0000"
        blocks = {
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": f"../resolveuid/{uid}",
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    }
                },
            }
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            f"../resolveuid/{uid}",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            f"../resolveuid/{uid}",
        )

    def test_blocks_field_serialization_doesnt_update_stored_values(self):
        uid = IUUID(self.doc2)
        blocks = {
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "Volto also supports other APIs.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
        }
        value = self.serialize("blocks", blocks)
        self.assertNotEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            blocks["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
        )
        self.assertNotEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            blocks["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
        )

    def test_blocks_field_deserialization_resolves_paths_to_uids(self):
        uid = IUUID(self.doc2)
        blocks = {
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "Volto also supports other APIs.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "url": self.doc2.absolute_url(),
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
        }
        value = self.deserialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            f"../resolveuid/{uid}",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            f"../resolveuid/{uid}",
        )

    def test_keeps_url_if_unknown_path(self):
        blocks = {
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": self.portal.absolute_url() + "/foo",
                                "rel": "nofollow",
                                "url": self.portal.absolute_url() + "/foo",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    }
                },
            }
        }
        value = self.deserialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            self.portal.absolute_url() + "/foo",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.portal.absolute_url() + "/foo",
        )

    def test_path_keeps_suffix(self):
        uid = IUUID(self.doc2)
        blocks = {
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "entityMap": {
                        "0": {
                            "data": {
                                "href": self.doc2.absolute_url() + "/view",
                                "rel": "nofollow",
                                "url": self.doc2.absolute_url() + "/view",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    }
                },
            }
        }
        value = self.deserialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            f"../resolveuid/{uid}/view",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            f"../resolveuid/{uid}/view",
        )

    def test_blocks_field_serialization_resolves_uids_with_primary_field_url(self):
        logout()
        uid = IUUID(self.doc_primary_field_url)
        blocks = {
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "Volto also supports other APIs.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc_primary_field_url.absolute_url()
            + "/@@download/test_primary_namedfile_field",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc_primary_field_url.absolute_url()
            + "/@@download/test_primary_namedfile_field",
        )

    def test_blocks_field_serialization_resolves_uids_primary_url_with_edit_permission(
        self,
    ):
        uid = IUUID(self.doc_primary_field_url)
        blocks = {
            "07c273fc-8bfc-4e7d-a327-d513e5a945bb": {"@type": "title"},
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [{"key": 0, "length": 5, "offset": 0}],
                            "inlineStyleRanges": [],
                            "key": "68rve",
                            "text": "Volto also supports other APIs.",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {
                        "0": {
                            "data": {
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    },
                },
            },
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc_primary_field_url.absolute_url(),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc_primary_field_url.absolute_url(),
        )

    def test_resolveuid_with_primary_field_url_keeps_suffix(self):
        uid = IUUID(self.doc2)
        blocks = {
            "effbdcdc-253c-41a7-841e-5edb3b56ce32": {
                "@type": "text",
                "text": {
                    "entityMap": {
                        "0": {
                            "data": {
                                "rel": "nofollow",
                                "url": f"../resolveuid/{uid}/view",
                            },
                            "mutability": "MUTABLE",
                            "type": "LINK",
                        }
                    }
                },
            }
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc2.absolute_url() + "/view",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            self.doc2.absolute_url() + "/view",
        )
