# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.dexterity.fti import DexterityFTI
from plone.restapi.behaviors import ITiles
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from zope.interface import alsoProvides

import unittest


class TestTilesBehavior(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        login(self.portal, TEST_USER_NAME)
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        fti = DexterityFTI("tiledfolder")
        self.portal.portal_types._setObject("tiledfolder", fti)
        fti.klass = "plone.dexterity.content.Container"
        fti.behaviors = ("plone.tiles",)
        self.fti = fti
        alsoProvides(self.request, ITiles)

    def test_basic_fields(self):
        self.portal.invokeFactory(
            "tiledfolder", id="tiledfolder", title=u"Folder with tiles"
        )

        self.portal["tiledfolder"].tiles = {
            "uuid1": {"@type": "title"},
            "uuid2": {"@type": "description"},
        }

        self.portal["tiledfolder"].tiles_layout = {
            "uuid1": {"@type": "title"},
            "uuid2": {"@type": "description"},
        }

    def test_behavior_provides(self):
        self.portal.invokeFactory(
            "tiledfolder", id="tiledfolder", title=u"Folder with tiles"
        )

        ITiles.providedBy(self.portal["tiledfolder"])
