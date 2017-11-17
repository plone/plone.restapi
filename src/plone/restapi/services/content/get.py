# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter


class ContentGet(Service):
    """Returns a serialized content object.
    """

    def reply(self):
        serializer = queryMultiAdapter((self.context, self.request),
                                       ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))

        return serializer(version=self.request.get('version'))
