# -*- coding: utf-8 -*-
from plone.app.testing import logout
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedFile
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter


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
                    data=u"Spam and eggs",
                    contentType=u"text/plain",
                    filename=u"test.txt",
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
                                "href": "../resolveuid/{}".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}".format(uid),
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
            ]["href"],
            self.doc2.absolute_url(),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
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
                                "href": "../resolveuid/{}/view".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}/view".format(uid),
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
            self.doc2.absolute_url() + "/view",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            self.doc2.absolute_url() + "/view",
        )

    def test_resolveuid_gets_serialized_for_standard_fields(self):
        uid = IUUID(self.doc2)
        blocks = {
            "aaa": {
                "@type": "foo",
                "url": "../resolveuid/{}/view".format(uid),
            }
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["aaa"]["url"],
            self.doc2.absolute_url() + "/view",
        )

        blocks = {
            "aaa": {
                "@type": "foo",
                "href": "../resolveuid/{}/view".format(uid),
            }
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["aaa"]["href"],
            self.doc2.absolute_url() + "/view",
        )

    def test_resolveuid_serialize_take_care_of_primary_fields(self):
        logout()
        uid = IUUID(self.doc_primary_field_url)
        blocks = {
            "aaa": {
                "@type": "foo",
                "url": "../resolveuid/{}".format(uid),
            }
        }
        value = self.serialize("blocks", blocks)
        self.assertEqual(
            value["aaa"]["url"],
            self.doc_primary_field_url.absolute_url() + "/@@download/test_primary_namedfile_field",
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
                                "href": "../resolveuid/{}".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}".format(uid),
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
            "../resolveuid/{}".format(uid),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["url"],
            "../resolveuid/{}".format(uid),
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
                                "href": "../resolveuid/{}".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}".format(uid),
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
            ]["href"],
            blocks["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
        )
        self.assertNotEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            blocks["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
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
                                "href": self.doc2.absolute_url(),
                                "rel": "nofollow",
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
            ]["href"],
            "../resolveuid/{}".format(uid),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            "../resolveuid/{}".format(uid),
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
            ]["href"],
            "../resolveuid/{}/view".format(uid),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            "../resolveuid/{}/view".format(uid),
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
                                "href": "../resolveuid/{}".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}".format(uid),
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
            ]["href"],
            self.doc_primary_field_url.absolute_url()
            + "/@@download/test_primary_namedfile_field",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
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
                                "href": "../resolveuid/{}".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}".format(uid),
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
            ]["href"],
            self.doc_primary_field_url.absolute_url(),
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
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
                                "href": "../resolveuid/{}/view".format(uid),
                                "rel": "nofollow",
                                "url": "../resolveuid/{}/view".format(uid),
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
            self.doc2.absolute_url() + "/view",
        )
        self.assertEqual(
            value["effbdcdc-253c-41a7-841e-5edb3b56ce32"]["text"]["entityMap"]["0"][
                "data"
            ]["href"],
            self.doc2.absolute_url() + "/view",
        )
