# -*- coding: utf-8 -*-

""" Slot patch operations
"""

from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.locking.locking import is_locked
from zope.component import queryMultiAdapter


class SlotsPatch(Service):
    """Update one or all the slots"""

    def __init__(self, context, request):
        super(SlotsPatch, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        if self.params and len(self.params) > 0:
            return self.replySlot()

        if is_locked(self.context, self.request):
            self.request.response.setStatus(403)
            return dict(error=dict(type="Forbidden", message="Resource is locked."))

        deserializer = queryMultiAdapter(
            (self.context, self.request), IDeserializeFromJson
        )
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(
                error=dict(
                    message="Cannot deserialize type {}".format(
                        self.context.portal_type
                    )
                )
            )

        try:
            deserializer()
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        prefer = self.request.getHeader("Prefer")
        if prefer == "return=representation":
            self.request.response.setStatus(200)

            serializer = queryMultiAdapter(
                (self.context, self.request), ISerializeToJson
            )

            serialized_obj = serializer()
            return serialized_obj

        return self.reply_no_content()
