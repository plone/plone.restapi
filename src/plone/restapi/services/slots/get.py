# -*- coding: utf-8 -*-

from AccessControl.SecurityManagement import getSecurityManager
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.permissions import ModifySlotsPermission
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.services import Service
from plone.restapi.slots import Slot
from plone.restapi.slots.interfaces import ISlots
from plone.restapi.slots.interfaces import ISlotStorage
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import plone.protect
import transaction


# TODO: write expand
def is_true(val):
    if isinstance(val, bool):
        return val

    if val in ["true", "True", "1", 1]:
        return True
    elif val in ["false", "False", "0", 0]:
        return False

    return False


@implementer(IPublishTraverse)
class SlotsGet(Service):
    """Returns the available slots."""

    def __init__(self, context, request):
        super(SlotsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):

        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        self.engine = ISlots(self.context)
        self.slot_names = self.engine.discover_slots()
        self.editable_slots = self.engine.get_editable_slots()

        if self.params and len(self.params) > 0:
            return self.replySlot()

        sm = getSecurityManager()
        storage = ISlotStorage(self.context)

        adapter = getMultiAdapter(
            (self.context, storage, self.request), ISerializeToJson
        )
        is_full = self.request.form.get("full", False)
        result = adapter(is_full)

        # from plone.restapi.serializer.converters import json_compatible
        # result["edit_slots"] = json_compatible(sorted(self.editable_slots))

        if sm.checkPermission(ModifySlotsPermission, self.context):
            result["can_manage_slots"] = True

        for k, v in result["items"].items():
            result["items"][k]["edit"] = k in self.editable_slots

        # support expandable elements for slots. For DX Content this is done in the
        # serializer, we do it here to keep the API limited
        result.update(expandable_elements(self.context, self.request))

        return result

    def replySlot(self):
        name = self.params[0]

        if name not in self.slot_names:
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Slot "{}" could not be found.'.format(self.params[0]),
            }

        marker = object()
        storage = ISlotStorage(self.context)
        slot = storage.get(name, marker)

        if slot is marker:  # if slot is not on this level, we create a fake one
            slot = Slot()  # TODO: replace with a DummyProxySlot
            slot.__parent__ = self.storage
            slot.__name__ = name

        result = getMultiAdapter((self.context, slot, self.request), ISerializeToJson)(
            self.request.form.get("full", False)
        )

        result["edit"] = name in self.editable_slots

        transaction.doom()  # avoid writing on read
        return result
