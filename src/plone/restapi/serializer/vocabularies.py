# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.interfaces import ITokenizedTerm
from zope.schema.interfaces import IVocabulary


@implementer(ISerializeToJson)
@adapter(IVocabulary, Interface)
class SerializeVocabularyToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, vocabulary_id):
        vocabulary = self.context
        serialized_terms = []
        for term in vocabulary:
            serializer = getMultiAdapter((term, self.request),
                                         interface=ISerializeToJson)
            serialized_terms.append(serializer(vocabulary_id))

        return {
            '@id': vocabulary_id,
            'terms': serialized_terms
        }


@implementer(ISerializeToJson)
@adapter(ITokenizedTerm, Interface)
class SerializeTermToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, vocabulary_id):
        term = self.context
        token = term.token
        title = term.title if ITitledTokenizedTerm.providedBy(term) else token
        return {
            '@id': '{}/{}'.format(vocabulary_id, token),
            'token': token,
            'title': title
        }
