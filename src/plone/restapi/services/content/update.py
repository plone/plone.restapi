# -*- coding: utf-8 -*-
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter


class ContentPatch(Service):
    """Updates an existing content object.
    """

    def reply(self):
        deserializer = queryMultiAdapter((self.context, self.request),
                                         IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                message='Cannot deserialize type {}'.format(
                    self.context.portal_type)))

        try:
            deserializer()
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='DeserializationError',
                message=str(e)))

        # TODO: alternativley return the patched object with a 200
        self.request.response.setStatus(204)
        return None
