# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory
from zope.component import getUtilitiesFor


class VocabulariesGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(VocabulariesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@vocabularies as parameters
        self.params.append(name)
        return self

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {
            'error': {
                'type': type,
                'message': message
            }
        }

    def reply(self):
        if len(self.params) == 0:
            return [
                {
                    '@id': '{}/@vocabularies/{}'.format(
                        self.context.absolute_url(),
                        vocab[0]
                    ),
                    'title': vocab[0]
                }
                for vocab in getUtilitiesFor(IVocabularyFactory)
            ]

        name = self.params[0]
        try:
            factory = getUtility(IVocabularyFactory, name=name)
        except ComponentLookupError:
            return self._error(
                404, "Not Found",
                "The vocabulary '{}' does not exist".format(name)
            )

        vocabulary = factory(self.context)
        vocabulary_name = self.params[0]
        serializer = getMultiAdapter(
            (vocabulary, self.request),
            interface=ISerializeToJson
        )
        return serializer(
            '{}/@vocabularies/{}'.format(
                self.context.absolute_url(),
                vocabulary_name
            )
        )
