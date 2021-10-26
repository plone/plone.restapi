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


class TestContentBlocks(unittest.TestCase):

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
        behavior_list.append("plone.leadimage")
        fti.behaviors = tuple(behavior_list)

        self.doc = createContentInContainer(
            self.portal, "Document", id="doc", title="A document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

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
