# -*- coding: utf-8 -*-
from AccessControl.interfaces import IRoleManager

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

        data = serializer(version=self.request.get('version'))
        if IRoleManager.providedBy(self.context):
            data['sharing'] = {
                '@id': '{}/@sharing'.format(self.context.absolute_url()),
                'title': 'Sharing',
                }
        return data
