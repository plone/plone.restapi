from AccessControl import getSecurityManager


try:
    from plone.app.vocabularies.security import DEFAULT_PERMISSION
    from plone.app.vocabularies.security import PERMISSIONS
except ImportError:
    from plone.app.content.browser.vocabulary import DEFAULT_PERMISSION
    from plone.app.content.browser.vocabulary import PERMISSIONS

from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import ComponentLookupError
from zope.component import getMultiAdapter
from zope.component import getUtilitiesFor
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


@implementer(IPublishTraverse)
class VocabulariesGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@vocabularies as parameters
        self.params.append(name)
        return self

    def _error(self, status, type, message):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message}}

    def _has_permission_to_access_vocabulary(self, vocabulary_name):
        """Check if user is authorized to access built-in vocabulary

        default permission for all vocabularies, built-in and others, was
          <permission
            id="plone.restapi.vocabularies"
            title="plone.restapi: Access Plone vocabularies"
            />
        """
        if vocabulary_name in PERMISSIONS:
            sm = getSecurityManager()
            return sm.checkPermission(
                PERMISSIONS.get(vocabulary_name, DEFAULT_PERMISSION), self.context
            )
        return True

    def reply(self):
        # return list of all vocabularies
        if len(self.params) == 0:
            return [
                {
                    "@id": "{}/@vocabularies/{}".format(
                        self.context.absolute_url(), vocab[0]
                    ),
                    "title": vocab[0],
                }
                for vocab in getUtilitiesFor(IVocabularyFactory)
            ]

        # return single vocabulary by name
        vocabulary_name = self.params[0]
        if not self._has_permission_to_access_vocabulary(vocabulary_name):
            return self._error(
                403,
                "Not authorized",
                (
                    f"You are not authorized to access "
                    f"the vocabulary '{vocabulary_name}'."
                ),
            )

        try:
            factory = getUtility(IVocabularyFactory, name=vocabulary_name)
        except ComponentLookupError:
            return self._error(
                404, "Not Found", f"The vocabulary '{vocabulary_name}' does not exist"
            )

        vocabulary = factory(self.context)
        serializer = getMultiAdapter(
            (vocabulary, self.request), interface=ISerializeToJson
        )
        return serializer(
            f"{self.context.absolute_url()}/@vocabularies/{vocabulary_name}"
        )
