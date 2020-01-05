# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import queryUtility

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
            self.portal, u"Document", id=u"doc", title=u"A document"
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
