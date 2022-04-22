"""
Test the blocks Dexterity behavior.
"""

from plone.app.testing import login
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.fti import DexterityFTI
from plone.restapi import testing
from plone.restapi.behaviors import IBlocks


class TestBlocksBehavior(testing.PloneRestAPILoggedInTestCase):
    """
    Test the blocks Dexterity behavior.
    """

    def setUp(self):
        """
        Set up a new content type to test against.
        """
        super().setUp()
        login(self.portal, TEST_USER_NAME)

        fti = DexterityFTI("blocksfolder")
        self.portal.portal_types._setObject("blocksfolder", fti)
        fti.klass = "plone.dexterity.content.Container"
        fti.behaviors = ("volto.blocks",)

    def test_basic_fields(self):
        self.portal.invokeFactory(
            "blocksfolder", id="blocksfolder", title="Folder with blocks"
        )

        self.portal["blocksfolder"].blocks = {
            "uuid1": {"@type": "title"},
            "uuid2": {"@type": "description"},
        }

        self.portal["blocksfolder"].blocks_layout = {
            "uuid1": {"@type": "title"},
            "uuid2": {"@type": "description"},
        }

    def test_behavior_provides(self):
        self.portal.invokeFactory(
            "blocksfolder", id="blocksfolder", title="Folder with blocks"
        )

        assert IBlocks.providedBy(self.portal["blocksfolder"])
