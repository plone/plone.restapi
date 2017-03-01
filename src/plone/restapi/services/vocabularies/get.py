# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


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
        return {'error': {'type': type,
                          'message': message}}

    def reply(self):
        if len(self.params) != 1:
            return self._error(
                400, "Vocabulary name required",
                "Must supply the dotted name of the vocabulary in the url")

        name = self.params[0]
        try:
            factory = getUtility(IVocabularyFactory, name=name)
        except ComponentLookupError:
            return self._error(
                404, "Not Found",
                "The vocabulary '{}' does not exist".format(name))

        vocabulary = factory(self.context)
        vocabulary_name = self.params[0]
        serializer = getMultiAdapter((vocabulary, self.request),
                                     interface=ISerializeToJson)
        return serializer('{}/@vocabularies/{}'.format(
            self.context.absolute_url(), vocabulary_name))
