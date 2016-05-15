# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.interfaces import ISerializeToJson
from zope.component import queryMultiAdapter


class ContentGet(Service):
    """Returns a serialized content object.
    """

    def render(self):
        serializer = queryMultiAdapter((self.context, self.request),
                                       ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))

        serialized_content = serializer()

        frame = self.request.form.get('frame')
        if frame == 'object':
            doc = self._frame_response_object(serialized_content)
        else:
            doc = serialized_content
        return doc

    def _frame_response_object(self, serialized_content):

        doc = {
            'fields': serialized_content,
        }

        context_url = self.context.absolute_url()

        doc['template'] = 'index'
        doc['versions'] = {'@id': '/'.join((context_url, 'versions_/'))}
        doc['workflow'] = {'@id': '/'.join((context_url, 'workflow_/'))}
        doc['actions'] = {'@id': '/'.join((context_url, 'actions_/'))}

        doc['@context'] = serialized_content.pop('@context')
        doc['@id'] = serialized_content.pop('@id')
        doc['@type'] = serialized_content.pop('@type')

        return doc
