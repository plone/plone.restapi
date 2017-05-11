# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.rest.traverse import RESTWrapper
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ConversationListGet(Service):

    def reply(self):
        url = self.request.URL
        return [
            {
                '@id': url + '/default',
                'comments': url + '/default/@comments/',
            },
        ]

    def publishTraverse(self, request, name):
        # Try to get a conversation, or defer for further traversal
        path = '++conversation++' + name
        conversation = self.context.restrictedTraverse(path)
        if conversation is not None:
            return RESTWrapper(ConversationWrapper(conversation), request)

        return super(ConversationListGet, self).publishTraverse(request, name)


class ConversationWrapper(object):
    # The sole reason for this to exist, is because the conversation's
    # __getitem__ implementation doesn't raise KeyError for faulty or
    # non-existing conversations.

    def __init__(self, context):
        self.context = context

    def __getattr__(self, name):
        # Delegate attribute access to the wrapped object
        # Needed for security checks in ZPublisher traversal
        return getattr(self.context, name)

    def __getitem__(self, key):
        value = self.context[key]
        if value is None:
            raise KeyError(key)
        return value


class ConversationGet(Service):

    def reply(self):
        return {'a single': 'conversation'}
