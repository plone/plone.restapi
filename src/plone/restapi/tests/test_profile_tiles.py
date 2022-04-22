"""
Test the Rest API handling of profile tiles in blocks.
"""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.behaviors import IBlocks
from plone.restapi import testing
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING
from Products.CMFCore.utils import getToolByName


class TestProfileBlocks(testing.PloneRestAPILoggedInTestCase):
    """
    Test the Rest API handling of profile tiles in blocks.
    """

    layer = PLONE_RESTAPI_BLOCKS_INTEGRATION_TESTING

    def setUp(self):
        """
        Make the test user a normal portal member without elevated permissions.
        """
        super().setUp()

        setRoles(self.portal, TEST_USER_ID, ["Member"])

    def test_document_type_has_blocks_behavior_enabled(self):
        self.portal.invokeFactory(
            "Document", id="blocksdoc", title="Document with blocks"
        )
        IBlocks.providedBy(self.portal["blocksdoc"])

    def test_plone_restapi_base_profile_applied(self):
        uf = getToolByName(self.portal, "acl_users")
        self.assertTrue("jwt_auth" in uf)
