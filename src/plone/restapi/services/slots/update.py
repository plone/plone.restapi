# -*- coding: utf-8 -*-

""" Slot patch operations
"""

from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISlots
from plone.restapi.services import Service
from plone.restapi.services.locking.locking import is_locked
from zope.component import getMultiAdapter
from zope.event import notify
from zope.lifecycleevent import ObjectModifiedEvent


class SlotsPatch(Service):
    """Update one or all the slots"""

    def __init__(self, context, request):
        super(SlotsPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        if is_locked(self.context, self.request):
            self.request.response.setStatus(403)
            return dict(error=dict(type="Forbidden", message="Resource is locked."))

        if self.params and len(self.params) > 0:
            return self.replySlot()

        storage = ISlots(self.context)

        deserializer = getMultiAdapter(
            (self.context, storage, self.request), IDeserializeFromJson
        )

        try:
            deserializer()
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        notify(ObjectModifiedEvent(self.context))

        prefer = self.request.getHeader("Prefer")
        if prefer == "return=representation":
            self.request.response.setStatus(200)

            serializer = getMultiAdapter(
                (self.context, storage, self.request), ISerializeToJson
            )

            serialized_obj = serializer()
            return serialized_obj

        return self.reply_no_content()

    def replySlot(self):
        name = self.params[0]
        storage = ISlots(self.context)
        slot = storage[name]

        deserializer = getMultiAdapter(
            (self.context, slot, self.request), IDeserializeFromJson
        )
        try:
            deserializer()
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        notify(ObjectModifiedEvent(self.context))

        prefer = self.request.getHeader("Prefer")
        if prefer == "return=representation":
            self.request.response.setStatus(200)

            serializer = getMultiAdapter(
                (self.context, slot, self.request), ISerializeToJson
            )

            serialized_obj = serializer(name)
            return serialized_obj

        return self.reply_no_content()
