# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi.bbb import IEditingSchema
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.uuid.interfaces import IUUID
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

import transaction
import unittest


class TestLinkIntegrity(unittest.TestCase):
    layer = PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.doc1 = createContentInContainer(
            self.portal, "Document", id="doc-1", title="First document"
        )
        self.doc2 = createContentInContainer(
            self.portal, "Document", id="doc-2", title="Second document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_required_uids(self):
        response = self.api_session.get("/@linkintegrity")

        self.assertEqual(response.status_code, 400)

    def test_return_no_breaches_for_non_referenced_objects(self):
        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [self.doc1.UID()]}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["breaches"], [])

    def test_return_right_breaches_for_reference_field(self):
        intids = getUtility(IIntIds)
        self.doc1.relatedItems = [RelationValue(intids.getId(self.doc2))]
        notify(ObjectModifiedEvent(self.doc1))
        transaction.commit()

        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [self.doc2.UID()]}
        )
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["@id"], self.doc2.absolute_url())

        breaches = result[0]["breaches"]
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0]["uid"], IUUID(self.doc1))
        self.assertEqual(breaches[0]["@id"], self.doc1.absolute_url())

    def test_do_not_return_breaches_if_check_is_disabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IEditingSchema, prefix="plone")
        settings.enable_link_integrity_checks = False
        intids = getUtility(IIntIds)
        self.doc1.relatedItems = [RelationValue(intids.getId(self.doc2))]
        notify(ObjectModifiedEvent(self.doc1))
        transaction.commit()

        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [self.doc2.UID()]}
        )
        breaches = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(breaches, [])

    def test_return_right_breaches_for_blocks(self):
        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [self.doc2.UID()]}
        )
        result = response.json()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["breaches"], [])

        # create a new content with relations
        uid = IUUID(self.doc2)
        doc_with_rel = createContentInContainer(
            self.portal,
            "Document",
            id="doc-with-rel",
            title="Document with relations",
            blocks={
                "block-uuid1": {
                    "@type": "text",
                    "text": {
                        "blocks": [{"text": "This is a link to second doc "}],
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
                }
            },
        )
        transaction.commit()

        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [self.doc2.UID()]}
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["@id"], self.doc2.absolute_url())

        breaches = result[0]["breaches"]
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0]["uid"], IUUID(doc_with_rel))
        self.assertEqual(breaches[0]["@id"], doc_with_rel.absolute_url())

    def test_return_breaches_for_contents_in_subfolders(self):
        # create a folder structure

        createContentInContainer(self.portal, "Folder", id="level1")
        createContentInContainer(self.portal["level1"], "Folder", id="level2")

        uid = IUUID(self.doc2)
        doc_in_folder = createContentInContainer(
            self.portal["level1"]["level2"],
            "Document",
            id="doc-in-folder",
            title="Document in folder",
            blocks={
                "block-uuid1": {
                    "@type": "text",
                    "text": {
                        "blocks": [{"text": "This is a link to second doc "}],
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
                }
            },
        )
        transaction.commit()

        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [self.doc2.UID()]}
        )

        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["@id"], self.doc2.absolute_url())

        breaches = result[0]["breaches"]
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0]["uid"], IUUID(doc_in_folder))
        self.assertEqual(breaches[0]["@id"], doc_in_folder.absolute_url())

    def test_return_items_total_in_subfolders(self):
        # create a folder structure
        level1 = createContentInContainer(self.portal, "Folder", id="level1")
        createContentInContainer(self.portal["level1"], "Folder", id="level2")
        transaction.commit()

        # get linkintegrity info for the folder
        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [level1.UID()]}
        )

        # we don't expect any links but we still want information
        # about how many contained items will be deleted
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["@id"], level1.absolute_url())
        self.assertEqual(result[0]["breaches"], [])
        self.assertEqual(result[0]["items_total"], 1)

    def test_tree_breaches_no_duplicates(self):
        # /target_parent/target_child
        target_parent = createContentInContainer(
            self.portal, "Folder", id="target-parent"
        )
        target_child = createContentInContainer(
            target_parent, "Document", id="target-child"
        )
        target_parent_uid = IUUID(target_parent)
        target_child_uid = IUUID(target_child)

        source_a = createContentInContainer(
            self.portal,
            "Document",
            id="source-a",
            title="Source A",
            blocks={
                "block-uuid1": {
                    "@type": "text",
                    "text": {
                        "blocks": [{"text": "some link"}],
                        "entityMap": {
                            "0": {
                                "data": {
                                    "href": f"../resolveuid/{target_parent_uid}",
                                    "rel": "nofollow",
                                    "url": f"../resolveuid/{target_parent_uid}",
                                },
                                "mutability": "MUTABLE",
                                "type": "LINK",
                            }
                        },
                    },
                },
                "block-uuid2": {
                    "@type": "text",
                    "text": {
                        "blocks": [{"text": "some other link"}],
                        "entityMap": {
                            "0": {
                                "data": {
                                    "href": f"../resolveuid/{target_child_uid}",
                                    "rel": "nofollow",
                                    "url": f"../resolveuid/{target_child_uid}",
                                },
                                "mutability": "MUTABLE",
                                "type": "LINK",
                            }
                        },
                    },
                },
            },
        )

        source_b = createContentInContainer(
            self.portal,
            "Document",
            id="source-b",
            title="Source B",
            blocks={
                "block-uuid3": {
                    "@type": "text",
                    "text": {
                        "blocks": [{"text": "some link"}],
                        "entityMap": {
                            "0": {
                                "data": {
                                    "href": f"../resolveuid/{target_parent_uid}",
                                    "rel": "nofollow",
                                    "url": f"../resolveuid/{target_parent_uid}",
                                },
                                "mutability": "MUTABLE",
                                "type": "LINK",
                            }
                        },
                    },
                }
            },
        )

        source_c = createContentInContainer(
            self.portal,
            "Document",
            id="source-c",
            title="Source C",
            blocks={
                "block-uuid4": {
                    "@type": "text",
                    "text": {
                        "blocks": [{"text": "some other link"}],
                        "entityMap": {
                            "0": {
                                "data": {
                                    "href": f"../resolveuid/{target_child_uid}",
                                    "rel": "nofollow",
                                    "url": f"../resolveuid/{target_child_uid}",
                                },
                                "mutability": "MUTABLE",
                                "type": "LINK",
                            }
                        },
                    },
                },
            },
        )

        transaction.commit()

        response = self.api_session.get(
            "/@linkintegrity", params={"uids": [target_parent_uid]}
        )

        results = response.json()
        self.assertEqual(
            [
                {
                    "@id": target_parent.absolute_url(),
                    "@type": "Folder",
                    "breaches": [
                        {
                            "@id": source_a.absolute_url(),
                            "title": "Source A",
                            "uid": IUUID(source_a),
                        },
                        {
                            "@id": source_b.absolute_url(),
                            "title": "Source B",
                            "uid": IUUID(source_b),
                        },
                    ],
                    "description": "",
                    "items_total": 1,
                    "review_state": "private",
                    "title": "",
                    "type_title": "Folder",
                },
                {
                    "@id": target_child.absolute_url(),
                    "@type": "Document",
                    "breaches": [
                        {
                            "@id": source_a.absolute_url(),
                            "title": "Source A",
                            "uid": IUUID(source_a),
                        },
                        {
                            "@id": source_c.absolute_url(),
                            "title": "Source C",
                            "uid": IUUID(source_c),
                        },
                    ],
                    "description": "",
                    "items_total": 0,
                    "review_state": "private",
                    "title": "",
                    "type_title": "Page",
                },
            ],
            results,
        )
