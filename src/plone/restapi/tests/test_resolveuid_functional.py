# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.fti import DexterityFTI
from plone.restapi.behaviors import IBlocks
from plone.uuid.interfaces import IUUID

from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.interface import alsoProvides

import transaction
import unittest


class TestResolveUIDFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        fti = DexterityFTI("blockspage")
        self.portal.portal_types._setObject("blockspage", fti)
        fti.klass = "plone.dexterity.content.Container"
        fti.behaviors = ("volto.blocks",)
        self.fti = fti
        alsoProvides(self.request, IBlocks)
        self.portal_url = self.portal.absolute_url()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory("Document", id="target", title="Target")
        self.target = self.portal.target
        self.target_uuid = IUUID(self.target)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_resolveuid(self):
        self.api_session.post(
            "/",
            json={
                "title": "Document",
                "@type": "blockspage",
                "blocks": {
                    "ca5908a5-3f58-4cd5-beb7-9bd1539d6744": {"@type": "title"},
                    "791bf004-7c88-4278-8490-13b85c3fa4b4": {
                        "@type": "text",
                        "text": {
                            "blocks": [
                                {
                                    "key": "3bnq6",
                                    "text": "Link",
                                    "type": "unstyled",
                                    "depth": 0,
                                    "inlineStyleRanges": [],
                                    "entityRanges": [
                                        {"offset": 0, "length": 4, "key": 0}
                                    ],
                                    "data": {},
                                }
                            ],
                            "entityMap": {
                                "0": {
                                    "type": "LINK",
                                    "mutability": "MUTABLE",
                                    "data": {
                                        "url": "{}/target".format(self.portal_url)
                                    },
                                }
                            },
                        },
                    },
                },
                "blocks_layout": {
                    "items": [
                        "ca5908a5-3f58-4cd5-beb7-9bd1539d6744",
                        "791bf004-7c88-4278-8490-13b85c3fa4b4",
                    ]
                },
            },
        )
        transaction.commit()
        self.assertEqual(
            "../resolveuid/{}".format(self.target_uuid),
            self.portal.document.blocks.get("791bf004-7c88-4278-8490-13b85c3fa4b4")
            .get("text")
            .get("entityMap")
            .get("0")
            .get("data")
            .get("url"),
        )
