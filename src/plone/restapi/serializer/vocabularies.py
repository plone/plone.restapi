from plone.restapi.batching import HypermediaBatch
from plone.restapi.bbb import safe_text
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IIterableSource
from zope.schema.interfaces import ITitledTokenizedTerm
from zope.schema.interfaces import ITokenizedTerm
from zope.schema.interfaces import IVocabulary


@implementer(ISerializeToJson)
class SerializeVocabLikeToJson:
    """Base implementation to serialize vocabularies and sources to JSON.

    Implements server-side filtering as well as batching.
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, vocabulary_id):
        vocabulary = self.context
        title = safe_text(self.request.form.get("title", ""))
        token = self.request.form.get("token", "")
        tokens = self.request.form.get("tokens", [])
        b_size = self.request.form.get("b_size", "")

        terms = []
        for term in vocabulary:
            if title and token:
                self.request.response.setStatus(400)
                return dict(
                    error=dict(
                        type="Invalid parameters",
                        message="You can not filter by title and token at the same time.",
                    )  # noqa
                )

            if token:
                # the token parameter was deprecated in plone.restapi 8
                # undeprecated in plone.restapi 9
                if token.lower() != term.token.lower():
                    continue
                terms.append(term)
            elif tokens:
                if isinstance(tokens, str):
                    tokens = [tokens]
                for item in tokens:
                    if item.lower() != term.token.lower():
                        continue
                    terms.append(term)
            else:
                term_title = safe_text(getattr(term, "title", None) or "")
                if (
                    title.lower()
                    not in translate(term_title, context=self.request).lower()
                ):
                    continue
                terms.append(term)

        serialized_terms = []

        # Do not batch parameter is set
        if b_size == "-1":
            for term in terms:
                serializer = getMultiAdapter(
                    (term, self.request), interface=ISerializeToJson
                )
                serialized_terms.append(serializer())
            return {"@id": vocabulary_id, "items": serialized_terms}

        batch = HypermediaBatch(self.request, terms)

        for term in batch:
            serializer = getMultiAdapter(
                (term, self.request), interface=ISerializeToJson
            )
            serialized_terms.append(serializer())

        result = {
            "@id": batch.canonical_url,
            "items": serialized_terms,
            "items_total": batch.items_total,
        }
        links = batch.links
        if links:
            result["batching"] = links
        return result


@adapter(IVocabulary, Interface)
class SerializeVocabularyToJson(SerializeVocabLikeToJson):
    """Serializes IVocabulary to JSON."""


@adapter(IIterableSource, Interface)
class SerializeSourceToJson(SerializeVocabLikeToJson):
    """Serializes IIterableSource to JSON."""


@implementer(ISerializeToJson)
@adapter(ITokenizedTerm, Interface)
class SerializeTermToJson:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        term = self.context
        token = term.token
        title = term.title if ITitledTokenizedTerm.providedBy(term) else token
        if isinstance(title, bytes):
            title = title.decode("UTF-8")
        return {"token": token, "title": translate(title, context=self.request)}
