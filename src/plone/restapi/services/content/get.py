# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from plone.rest import Service
from plone.restapi.interfaces import ISerializeToJson
from zope.component import queryMultiAdapter


class ContentGet(Service):
    """Returns a serialized content object.
    """

    def render(self):
        sm = getSecurityManager()
        if not sm.checkPermission('View', self.context):
            raise Unauthorized

        serializer = queryMultiAdapter((self.context, self.request),
                                       ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))

        return serializer()
