"""
Test content blocks.
"""

from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import createContentInContainer
from plone.restapi import testing
from zope.component import queryUtility

import transaction


class TestContentBlocks(testing.PloneRestAPIBrowserTestCase):
    """
    Test content blocks.
    """

    def setUp(self):
        """
        Enable the blocks behavior for a content type and instance.
        """
        super().setUp()

        fti = queryUtility(IDexterityFTI, name="Document")
        behavior_list = [a for a in fti.behaviors]
        behavior_list.append("volto.blocks")
        behavior_list.append("plone.leadimage")
        fti.behaviors = tuple(behavior_list)

        self.doc = createContentInContainer(
            self.portal, "Document", id="doc", title="A document"
        )
        transaction.commit()

    def test_patch_blocks_list(self):
        response = self.api_session.patch(
            "/doc",
            json={
                "blocks": {
                    "uuid1": {"@type": "title"},
                    "uuid2": {"@type": "description"},
                }
            },
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/doc")
        response = response.json()

        self.assertEqual(
            response["blocks"],
            {"uuid1": {"@type": "title"}, "uuid2": {"@type": "description"}},
        )

    def test_patch_blocks_layout(self):
        response = self.api_session.patch(
            "/doc", json={"blocks_layout": {"items": ["#uuid1", "#uuid2"]}}
        )

        self.assertEqual(response.status_code, 204)

        response = self.api_session.get("/doc")
        response = response.json()

        self.assertEqual(response["blocks_layout"], {"items": ["#uuid1", "#uuid2"]})

    def test_get_blocks_layout_schema(self):
        response = self.api_session.get("/@types/Document")

        self.assertEqual(response.status_code, 200)
        response = response.json()

    # These are not failing because the patch operations doesn't validate
    # fields right now
    # def test_patch_blocks_list_wrong_type(self):
    #     response = self.api_session.patch(
    #         '/doc',
    #         json={
    #             "blocks": [{'uuid1': {'@type': 'title'}}]
    #         })
    #     self.assertEqual(response.status_code, 500)

    # def test_patch_blocks_layout_wrong_type(self):
    #     response = self.api_session.patch(
    #         '/doc',
    #         json={
    #             "blocks_layout": {'uuid1': {'@type': 'title'}}
    #         })
    #     self.assertEqual(response.status_code, 500)
