# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from plone.restapi.upgrades.ordering import (
    ensure_child_ordering_object_ids_are_native_strings,
)

import unittest
import six


class TestUpgradeOrdering(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

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
        ordering.moveObjectsToBottom([six.text_type("doc1")])

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
        ordering.moveObjectsToBottom([six.text_type("doc1")])

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
