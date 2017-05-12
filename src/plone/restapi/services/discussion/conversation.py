# -*- coding: utf-8 -*-
from plone.app.discussion.interfaces import IConversation
from plone.rest.traverse import RESTWrapper
from plone.restapi.services import Service
from zope.component import getAdapters
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ConversationListGet(Service):

    def reply(self):
        url = self.request.URL

        def transform(adapters):
            for name, conversation in adapters:
                if not conversation.enabled():
                    continue

                name = name or 'default'
                data = {
                    '@id': '{}/{}'.format(url, name),
                    'comments': '{}/{}/@comments'.format(url, name),
                }

                yield data

        adapters = getAdapters((self.context, ), IConversation)
        return list(transform(adapters))

    def publishTraverse(self, request, name):
        # Try to get a conversation, or defer for further traversal
        path = '++conversation++' + name
        # Do security checks later on.
        conversation = self.context.unrestrictedTraverse(path)
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
