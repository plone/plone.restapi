# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.utils import referencedRelationship
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
from plone.restapi.testing import RelativeSession
from plone.uuid.interfaces import IUUID
from unittest import TestCase
from zc.relation.interfaces import ICatalog
from zope.component import getUtility
from zope.intid.interfaces import IIntIds

import transaction


class TestBlocksLinkintegrity(TestCase):
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

    def retrieve_links(self, value):
        retriever = IRetriever(self.portal.doc1)
        return retriever.retrieveLinks()

    def test_links_retriever_return_internal_links_in_text_block(self):
        uid = IUUID(self.doc2)
        blocks = {
            "111": {"@type": "title"},
            "222": {
                "@type": "text",
                "text": {
                    "blocks": [{"key": "68rve", "text": "Example text"}],
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
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_return_internal_links_type_a_in_slate_block(self):
        uid = IUUID(self.doc2)
        resolve_uid_link = {
            "@id": f"../resolveuid/{uid}",
            "title": "Welcome to Plone",
        }
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [resolve_uid_link]
                                                }
                                            }
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }

        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_return_internal_links_type_link_in_slate_block(self):
        uid = IUUID(self.doc2)
        resolve_uid_link = f"../resolveuid/{uid}"
        blocks = {
            "abc": {
                "@type": "slate",
                "plaintext": "Frontpage content here",
                "value": [
                    {
                        "children": [
                            {"text": "Frontpage "},
                            {
                                "children": [{"text": "content "}],
                                "data": {
                                    "url": resolve_uid_link,
                                },
                                "type": "link",
                            },
                            {"text": "here"},
                        ],
                        "type": "h2",
                    }
                ],
            }
        }

        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_return_internal_links_in_generic_block(self):
        uid = IUUID(self.doc2)
        blocks = {"111": {"@type": "foo", "href": "../resolveuid/{}".format(uid)}}
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_return_internal_links_in_generic_block_href_list(self):
        uid = IUUID(self.doc2)
        blocks = {"111": {"@type": "foo", "href": ["../resolveuid/{}".format(uid)]}}
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_return_internal_links_in_generic_block_href_id(self):
        uid = IUUID(self.doc2)
        blocks = {
            "111": {"@type": "foo", "href": [{"@id": "../resolveuid/{}".format(uid)}]}
        }
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_return_internal_links_in_text_block_once(self):
        uid = IUUID(self.doc2)
        blocks = {
            "111": {"@type": "title"},
            "222": {
                "@type": "text",
                "text": {
                    "blocks": [{"key": "68rve", "text": "Example text"}],
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
            "333": {
                "@type": "text",
                "text": {
                    "blocks": [{"key": "68rve", "text": "Another text"}],
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
            "444": {"@type": "foo", "href": "../resolveuid/{}".format(uid)},
        }
        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 1)
        self.assertIn("../resolveuid/{}".format(uid), value)

    def test_links_retriever_skip_empty_links(self):
        blocks = {
            "abc": {
                "@type": "slate",
                "plaintext": "Frontpage content here",
                "value": [
                    {
                        "children": [
                            {"text": "Frontpage "},
                            {
                                "children": [{"text": "content "}],
                                "data": {
                                    "url": None,
                                },
                                "type": "link",
                            },
                            {"text": "here"},
                        ],
                        "type": "h2",
                    }
                ],
            }
        }

        self.portal.doc1.blocks = blocks
        value = self.retrieve_links(blocks)

        self.assertEqual(len(value), 0)


class TestLinkintegrityForBlocks(TestCase):

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

    def get_back_references(self, item):
        catalog = getUtility(ICatalog)
        intids = getUtility(IIntIds)
        result = []
        for rel in catalog.findRelations(
            dict(
                to_id=intids.getId(aq_inner(item)),
                from_attribute=referencedRelationship,
            )
        ):
            obj = intids.queryObject(rel.from_id)
            if obj is not None:
                result.append(obj)
        return result

    def test_reference_correctly_set_for_text_blocks(self):
        self.assertEqual([], self.get_back_references(self.doc2))

        uid = IUUID(self.doc2)
        response = self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
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
                }
            },
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)
        self.assertEqual(back_references[0], self.doc1)

    def test_reference_correctly_unset_for_text_blocks(self):
        uid = IUUID(self.doc2)
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
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
                }
            },
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)

        # now unset reference
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "text",
                        "text": {
                            "blocks": [{"text": "This is a link to plone.org "}],
                            "entityMap": {
                                "0": {
                                    "data": {
                                        "href": "http://www.plone.org",
                                        "rel": "nofollow",
                                        "url": "http://www.plone.org",
                                    },
                                    "mutability": "MUTABLE",
                                    "type": "LINK",
                                }
                            },
                        },
                    }
                }
            },
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 0)

    def test_reference_correctly_set_for_slate_blocks(self):
        self.assertEqual([], self.get_back_references(self.doc2))

        uid = IUUID(self.doc2)
        resolve_uid_link = {
            "@id": f"../resolveuid/{uid}",
            "title": "Welcome to Plone",
        }
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [resolve_uid_link]
                                                }
                                            }
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }
        response = self.api_session.patch(
            "/doc-1",
            json={"blocks": blocks},
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)
        self.assertEqual(back_references[0], self.doc1)

    def test_reference_correctly_unset_for_slate_blocks(self):
        uid = IUUID(self.doc2)
        resolve_uid_link = {
            "@id": f"../resolveuid/{uid}",
            "title": "Welcome to Plone",
        }
        blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                    {
                                        "children": [{"text": "slate link"}],
                                        "data": {
                                            "link": {
                                                "internal": {
                                                    "internal_link": [resolve_uid_link]
                                                }
                                            }
                                        },
                                        "type": "a",
                                    },
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }
        self.api_session.patch(
            "/doc-1",
            json={"blocks": blocks},
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)

        # now unset reference
        unset_blocks = {
            "2caef9e6-93ff-4edf-896f-8c16654a9923": {
                "@type": "slate",
                "plaintext": "this is a slate link inside some text",
                "value": [
                    {
                        "children": [
                            {"text": "this is a "},
                            {
                                "children": [
                                    {"text": ""},
                                ],
                                "type": "strong",
                            },
                            {"text": " inside some text"},
                        ],
                        "type": "p",
                    }
                ],
            },
            "6b2be2e6-9857-4bcc-a21a-29c0449e1c68": {"@type": "title"},
        }
        self.api_session.patch(
            "/doc-1",
            json={"blocks": unset_blocks},
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 0)

    def test_reference_correctly_set_for_generic_blocks_with_href(self):
        self.assertEqual([], self.get_back_references(self.doc2))

        uid = IUUID(self.doc2)
        response = self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "foo",
                        "href": "../resolveuid/{}".format(uid),
                    }
                }
            },
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)
        self.assertEqual(back_references[0], self.doc1)

    def test_reference_correctly_unset_for_generic_blocks_with_href(self):
        uid = IUUID(self.doc2)
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "foo",
                        "href": "../resolveuid/{}".format(uid),
                    }
                }
            },
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)

        # now unset reference
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {"uuid1": {"@type": "foo", "href": "http://www.plone.org"}}
            },
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 0)

    def test_reference_correctly_set_for_generic_blocks_with_url(self):
        self.assertEqual([], self.get_back_references(self.doc2))

        uid = IUUID(self.doc2)
        response = self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "foo",
                        "url": "../resolveuid/{}".format(uid),
                    }
                }
            },
        )
        transaction.commit()
        self.assertEqual(response.status_code, 204)
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)
        self.assertEqual(back_references[0], self.doc1)

    def test_reference_correctly_unset_for_generic_blocks_with_url(self):
        uid = IUUID(self.doc2)
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "foo",
                        "url": "../resolveuid/{}".format(uid),
                    }
                }
            },
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 1)

        # now unset reference
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {"uuid1": {"@type": "foo", "href": "http://www.plone.org"}}
            },
        )
        transaction.commit()
        back_references = self.get_back_references(self.doc2)
        self.assertEqual(len(back_references), 0)

    def test_delete_confirm_info_return_right_values(self):
        uid = IUUID(self.doc2)
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
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
                }
            },
        )
        transaction.commit()
        links_info = self.doc2.restrictedTraverse("@@delete_confirmation_info")
        breaches = links_info.get_breaches()

        self.assertEqual(len(breaches), 1)
        self.assertEqual(len(breaches[0]["sources"]), 1)
        self.assertEqual(breaches[0]["sources"][0]["uid"], IUUID(self.doc1))

        # now try to unset internal link
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "text",
                        "text": {
                            "blocks": [{"text": "Now we set an external link"}],
                            "entityMap": {
                                "0": {
                                    "data": {
                                        "href": "http://www.plone.org",
                                        "rel": "nofollow",
                                        "url": "http://www.plone.org",
                                    },
                                    "mutability": "MUTABLE",
                                    "type": "LINK",
                                }
                            },
                        },
                    }
                }
            },
        )
        transaction.commit()
        links_info = self.doc2.restrictedTraverse("@@delete_confirmation_info")
        breaches = links_info.get_breaches()

        self.assertEqual(len(breaches), 0)
