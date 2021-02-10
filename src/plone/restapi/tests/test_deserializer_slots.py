from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.slots.interfaces import ISlotStorage
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from Products.CMFPlone.tests.PloneTestCase import PloneTestCase
from zope.component import getMultiAdapter


# from plone.api import portal
# from plone.restapi.slots import Slot
# from plone.restapi.slots import Slots
# from plone.restapi.slots.interfaces import ISlots
# from plone.restapi.slots.interfaces import ISlotSettings
# from zope.component import provideAdapter
# from zope.interface import implements
# from zope.interface import Interface


class TestSlotsEngineIntegration(PloneTestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        self.portal.acl_users.userFolderAddUser(
            'simple_member', 'slots_pw', ["Member"], []
        )

        self.portal.acl_users.userFolderAddUser(
            'editor_member', 'slots_pw', ["Editor"], []
        )

        self.make_content()

    def make_content(self):
        self.documents = createContentInContainer(
            self.portal, u"Folder", id=u"documents", title=u"Documents"
        )
        self.company = createContentInContainer(
            self.documents, u"Folder", id=u"company-a", title=u"Documents"
        )
        self.doc = createContentInContainer(
            self.company, u"Document", id=u"doc-1", title=u"Doc 1"
        )

    def test_deserialize_empty(self):
        storage = ISlotStorage(self.doc)
        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)
        deserializer()

        self.assertEqual(list(storage.keys()), [])

    def test_deserialize_put_one(self):
        storage = ISlotStorage(self.doc)
        deserializer = getMultiAdapter(
            (self.doc, storage, self.request), IDeserializeFromJson)
        deserializer({"left": {
            'blocks_layout': {'items': [3, 2, 5]},
            'blocks': {
                2: {'title': 'Second', 's:isVariantOf': 1},
                3: {'title': 'Third', '_v_inherit': True},
                5: {'title': 'Fifth', '_v_inherit': True},
            }
        }})

        self.assertEqual(list(storage.keys()), ['left'])
