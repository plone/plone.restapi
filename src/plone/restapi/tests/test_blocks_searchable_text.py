from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.interfaces import IDexterityItem
from plone.dexterity.utils import createContentInContainer
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockSearchableText
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import adapter
from zope.component import provideAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import transaction
import unittest


class TestSearchTextInBlocks(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        fti.behaviors = tuple(behavior_list)

        self.doc = createContentInContainer(
            self.portal, "Document", id="doc", title="A document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_search_text(self):
        response = self.api_session.patch(
            "/doc",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "text",
                        "text": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "acv4f",
                                    "text": "Plone " "text " "for " "block ",
                                    "type": "unstyled",
                                }
                            ],
                            "entityMap": {},
                        },
                    },
                    "uuid2": {
                        "@type": "text",
                        "text": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "1m9qt",
                                    "text": "Volto " "text " "for " "block ",
                                    "type": "unstyled",
                                }
                            ],
                            "entityMap": {},
                        },
                    },
                }
            },
        )

        self.assertEqual(response.status_code, 204)

        query = {"SearchableText": "Volto", "metadata_fields": "Title"}
        response = self.api_session.get("/@search", params=query)
        json_response = response.json()
        self.assertEqual(json_response["items_total"], 1)
        self.assertEqual(json_response["items"][0]["Title"], "A document")

        query = {"SearchableText": "Plone", "metadata_fields": "Title"}
        response = self.api_session.get("/@search", params=query)
        json_response = response.json()
        self.assertEqual(json_response["items_total"], 1)
        self.assertEqual(json_response["items"][0]["Title"], "A document")

    def test_register_block_searchabletext(self):
        @implementer(IBlockSearchableText)
        @adapter(IBlocks, IBrowserRequest)
        class TestSearchableTextAdapter:
            def __init__(self, context, request):
                self.context = context
                self.request = request

            def __call__(self, value):

                return "discovered: %s" % value["text"]

        provideAdapter(
            TestSearchableTextAdapter,
            (IDexterityItem, IBrowserRequest),
            name="test_block",
        )

        blocks = {
            "uuid1": {
                "@type": "text",
                "text": {
                    "blocks": [
                        {
                            "data": {},
                            "depth": 0,
                            "entityRanges": [],
                            "inlineStyleRanges": [],
                            "key": "acv4f",
                            "text": "Plone " "text " "for " "block ",
                            "type": "unstyled",
                        }
                    ],
                    "entityMap": {},
                },
            },
            "uuid3": {"@type": "test_block", "text": "sample text"},
        }

        self.doc.blocks = blocks
        from plone.indexer.interfaces import IIndexableObject
        from zope.component import queryMultiAdapter

        wrapper = queryMultiAdapter(
            (self.doc, self.portal.portal_catalog), IIndexableObject
        )

        assert "discovered: sample text" in wrapper.SearchableText

    def test_index_searchableText_value(self):
        response = self.api_session.patch(
            "/doc",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "text",
                        "text": {
                            "blocks": [
                                {
                                    "data": {},
                                    "depth": 0,
                                    "entityRanges": [],
                                    "inlineStyleRanges": [],
                                    "key": "acv4f",
                                    "text": "Plone " "text " "for " "block ",
                                    "type": "unstyled",
                                }
                            ],
                            "entityMap": {},
                        },
                    },
                    "uuid2": {
                        "@type": "custom_type",
                        "searchableText": "custom text foo",
                    },
                }
            },
        )

        self.assertEqual(response.status_code, 204)

        query = {"SearchableText": "Volto", "metadata_fields": "Title"}
        response = self.api_session.get("/@search", params=query)
        json_response = response.json()
        self.assertEqual(json_response["items_total"], 0)

        query = {"SearchableText": "Plone", "metadata_fields": "Title"}
        response = self.api_session.get("/@search", params=query)
        json_response = response.json()
        self.assertEqual(json_response["items_total"], 1)
        self.assertEqual(json_response["items"][0]["Title"], "A document")

        query = {"SearchableText": "custom", "metadata_fields": "Title"}
        response = self.api_session.get("/@search", params=query)
        json_response = response.json()
        self.assertEqual(json_response["items_total"], 1)
        self.assertEqual(json_response["items"][0]["Title"], "A document")

    def test_search_slate_text(self):
        """test_search_text."""
        self.doc.blocks = {
            "38541872-06c2-41c9-8709-37107e597b18": {
                "@type": "slate",
                "plaintext": "Under a new climatic regime, therefore",
                "value": [],
            },
            "4fcfeb9b-f73e-427c-9e06-2e4d53b06865": {
                "@type": "slate",
                "searchableText": "EEA Climate Change data centre",
                "value": [],
            },
        }
        self.doc.blocks_layout = [
            "38541872-06c2-41c9-8709-37107e597b18",
            "4fcfeb9b-f73e-427c-9e06-2e4d53b06865",
        ]
        self.portal.portal_catalog.indexObject(self.doc)

        query = {"SearchableText": "climatic"}
        results = self.portal.portal_catalog.searchResults(**query)
        self.assertEqual(len(results), 1)

        brain = results[0]
        self.assertEqual(brain.Title, "A document")

        query = {"SearchableText": "EEA"}
        results = self.portal.portal_catalog.searchResults(**query)
        self.assertEqual(len(results), 1)

        brain = results[0]
        self.assertEqual(brain.Title, "A document")
