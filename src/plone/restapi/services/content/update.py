# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from plone.rest import Service
from plone.restapi.deserializer import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import queryMultiAdapter


class ContentPatch(Service):
    """Updates an existing content object.
    """

    def render(self):
        sm = getSecurityManager()
        if not sm.checkPermission('Modify portal content', self.context):
            raise Unauthorized

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
