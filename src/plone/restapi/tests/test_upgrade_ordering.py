"""
Test Rest API handling folder ordering upgrades.
"""

from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi import testing
from plone.restapi.upgrades.ordering import (
    ensure_child_ordering_object_ids_are_native_strings,
)


class TestUpgradeOrdering(testing.PloneRestAPITestCase):
    """
    Test Rest API handling folder ordering upgrades.
    """

    def setUp(self):
        """
        Create content instances to test against.
        """
        super().setUp()

        self.folder = self.portal[
            self.portal.invokeFactory("Folder", id="folder1", title="Folder")
        ]
        for x in range(1, 4):
            self.folder.invokeFactory(
                "Document", id="doc" + str(x), title="Test doc " + str(x)
            )

    def test_upgrade_ensure_child_ordering_object_ids_are_native_strings(self):
        ordering = self.folder.getOrdering()

        # use incorrect type for ordering, results in mixed type ordering ids
        # on folder
        ordering.moveObjectsToBottom(["doc1"])

        ensure_child_ordering_object_ids_are_native_strings(self.folder)

        self.assertEqual(
            [
                "doc2",
                "doc3",
                "doc1",
            ],
            self.folder.objectIds(),  # noqa
        )

        # upgrade helper should ensure bytestring ids in python2 and do nothing
        # on python3
        for id_ in self.folder.objectIds():
            self.assertIsInstance(id_, str)

    def test_upgrade_can_be_called_with_nonetype(self):
        ensure_child_ordering_object_ids_are_native_strings(None)

    def test_upgrade_can_be_called_with_not_annotatable(self):
        ensure_child_ordering_object_ids_are_native_strings(object())

    def test_upgrade_view(self):
        ordering = self.folder.getOrdering()
        # use incorrect type for ordering, results in mixed type ordering ids
        # on folder
        ordering.moveObjectsToBottom(["doc1"])

        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        view = self.portal.restrictedTraverse("@@plone-restapi-upgrade-fix-ordering")
        view()

        self.assertEqual(
            [
                "doc2",
                "doc3",
                "doc1",
            ],
            self.folder.objectIds(),  # noqa
        )

        # upgrade helper should ensure bytestring ids in python2 and do nothing
        # on python3
        for id_ in self.folder.objectIds():
            self.assertIsInstance(id_, str)
