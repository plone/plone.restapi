from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import TEST_USER_ID
from plone.restapi.behaviors import IBlocks
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName

import unittest


class TestProfileBlocks(unittest.TestCase):

    layer = PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)

    def test_document_type_has_blocks_behavior_enabled(self):
        self.portal.invokeFactory(
            "Document", id="blocksdoc", title="Document with blocks"
        )
        IBlocks.providedBy(self.portal["blocksdoc"])

    def test_plone_restapi_base_profile_applied(self):
        uf = getToolByName(self.portal, "acl_users")
        self.assertTrue("jwt_auth" in uf)
