# -*- coding: utf-8 -*-
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.locking.locking import is_locked
from zope.component import queryMultiAdapter


class ContentPatch(Service):
    """Updates an existing content object."""

    def reply(self):

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
