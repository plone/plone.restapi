# -*- coding: utf-8 -*-
"""JsonSchema providers."""
from plone.app.textfield.interfaces import IRichText
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import get_querysource_url
from plone.restapi.types.utils import get_source_url
from plone.restapi.types.utils import get_vocabulary_url
from plone.restapi.types.utils import get_widget_params
from plone.schema import IEmail
from plone.schema import IJSONField
from z3c.formwidget.query.interfaces import IQuerySource
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IASCII
from zope.schema.interfaces import IASCIILine
from zope.schema.interfaces import IBool
from zope.schema.interfaces import IBytes
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IContextSourceBinder
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IDecimal
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFloat
from zope.schema.interfaces import IInt
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject
from zope.schema.interfaces import IPassword
from zope.schema.interfaces import IURI
from zope.schema.interfaces import ISet
from zope.schema.interfaces import IText
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import ITuple


@adapter(IField, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DefaultJsonSchemaProvider(object):
    def __init__(self, field, context, request):
        self.field = field.bind(context)
        self.context = context
        self.request = request

    def additional(self):
        """Additional info for field."""
        return {}

    def get_title(self):
        return translate(self.field.title, context=self.request)

    def get_description(self):
        if self.field.description is None:
            return u""

        return translate(self.field.description, context=self.request)

    def get_schema(self):
        """Get jsonschema for field.

        You should override `additional` method to provide more properties
        about the field."""
        schema = {
            "type": self.get_type(),
            "title": self.get_title(),
            "description": self.get_description(),
        }

        widget = self.get_widget()
        if widget:
            schema["widget"] = widget

        factory = self.get_factory()
        if factory:
            schema["factory"] = factory

        widget_options = self.get_widget_params()
        if widget_options:
            schema["widgetOptions"] = widget_options

        if self.field.default is not None:
            schema["default"] = self.field.default

        schema.update(self.additional())
        return schema

    def get_type(self):
        raise NotImplementedError

    def get_factory(self):
        return None

    def get_widget(self):
        return None

    def get_widget_params(self):
        all_params = get_widget_params([self.field.interface])
        params = all_params.get(self.field.getName(), {})
        if "vocabulary" in params:
            vocab_name = params["vocabulary"]
            params["vocabulary"] = {
                "@id": get_vocabulary_url(vocab_name, self.context, self.request)
            }
        return params


@adapter(IBytes, Interface, Interface)
@implementer(IJsonSchemaProvider)
class BytesLineJsonSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "string"

    def get_factory(self):
        return "Text line (String)"


@adapter(ITextLine, Interface, Interface)
@implementer(IJsonSchemaProvider)
class TextLineJsonSchemaProvider(DefaultJsonSchemaProvider):
    def additional(self):
        info = {}
        if self.field.min_length:
            info["minLength"] = self.field.min_length

        if self.field.max_length:
            info["maxLength"] = self.field.max_length

        return info

    def get_type(self):
        return "string"

    def get_factory(self):
        return "Text line (String)"


@adapter(IText, Interface, Interface)
@implementer(IJsonSchemaProvider)
class TextJsonSchemaProvider(TextLineJsonSchemaProvider):
    def get_widget(self):
        return "textarea"

    def get_factory(self):
        return "Text"


@adapter(IEmail, Interface, Interface)
@implementer(IJsonSchemaProvider)
class EmailJsonSchemaProvider(TextLineJsonSchemaProvider):
    def get_widget(self):
        return "email"

    def get_factory(self):
        return "Email"


@adapter(IPassword, Interface, Interface)
@implementer(IJsonSchemaProvider)
class PasswordJsonSchemaProvider(TextLineJsonSchemaProvider):
    def get_widget(self):
        return "password"

    def get_factory(self):
        return "Password"


@adapter(IURI, Interface, Interface)
@implementer(IJsonSchemaProvider)
class URIJsonSchemaProvider(TextLineJsonSchemaProvider):
    def get_widget(self):
        return "url"

    def get_factory(self):
        return "URL"


@adapter(IASCII, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ASCIIJsonSchemaProvider(TextLineJsonSchemaProvider):
    pass


@adapter(IASCIILine, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ASCIILineJsonSchemaProvider(TextLineJsonSchemaProvider):
    pass


@adapter(IFloat, Interface, Interface)
@implementer(IJsonSchemaProvider)
class FloatJsonSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "number"

    def additional(self):
        info = {}
        if self.field.min is not None:
            info["minimum"] = self.field.min

        if self.field.max is not None:
            info["maximum"] = self.field.max

        return info

    def get_factory(self):
        return "Floating-point number"


@adapter(IDecimal, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DecimalJsonSchemaProvider(FloatJsonSchemaProvider):
    pass


@adapter(IInt, Interface, Interface)
@implementer(IJsonSchemaProvider)
class IntegerJsonSchemaProvider(FloatJsonSchemaProvider):
    def get_type(self):
        return "integer"

    def get_factory(self):
        return "Integer"


@adapter(IBool, Interface, Interface)
@implementer(IJsonSchemaProvider)
class BoolJsonSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "boolean"

    def get_factory(self):
        return "Yes/No"


@adapter(ICollection, Interface, Interface)
@implementer(IJsonSchemaProvider)
class CollectionJsonSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "array"

    def get_factory(self):
        map = {
            "RelationList": "Relation List",
            "Set": "Multiple Choice",
            "List": "List",
            "Tuple": "Tuple",
        }

        for key, value in map.items():
            if key in self.field.__repr__():
                return value

        return "Collection"

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request), IJsonSchemaProvider
        )

        return value_type_adapter.get_schema()

    def additional(self):
        info = {}
        info["additionalItems"] = True
        if self.field.min_length:
            info["minItems"] = self.field.min_length

        if self.field.max_length:
            info["maxItems"] = self.field.max_length

        info["items"] = self.get_items()

        return info


@adapter(IList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ListJsonSchemaProvider(CollectionJsonSchemaProvider):
    def additional(self):
        info = super(ListJsonSchemaProvider, self).additional()
        if IChoice.providedBy(self.field.value_type):
            info["uniqueItems"] = True
        else:
            info["uniqueItems"] = False

        return info


@adapter(ISet, Interface, Interface)
@implementer(IJsonSchemaProvider)
class SetJsonSchemaProvider(CollectionJsonSchemaProvider):
    def additional(self):
        info = super(SetJsonSchemaProvider, self).additional()
        info["uniqueItems"] = True
        return info


@adapter(ITuple, Interface, Interface)
@implementer(IJsonSchemaProvider)
class TupleJsonSchemaProvider(SetJsonSchemaProvider):
    pass


@adapter(IChoice, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ChoiceJsonSchemaProvider(DefaultJsonSchemaProvider):

    # optionally prevent rendering all choices in the vocab,
    # ie relatedItems, which contains UUIDs for all content in the site.
    should_render_choices = True

    def get_type(self):
        return "string"

    def get_factory(self):
        map = {"RelationChoice": "Relation Choice", "Choice": "Choice"}

        for key, value in map.items():
            if key in self.field.__repr__():
                return value
        return "Choice"

    def additional(self):
        # Named global vocabulary
        vocab_name = getattr(self.field, "vocabularyName", None)
        if vocab_name:
            return {
                "vocabulary": {
                    "@id": get_vocabulary_url(vocab_name, self.context, self.request)
                }
            }

        # Maybe an unnamed vocabulary or source.
        vocabulary = getattr(self.field, "vocabulary", None)
        if IContextSourceBinder.providedBy(vocabulary):
            vocabulary = vocabulary(self.context)

        # Query source
        if IQuerySource.providedBy(vocabulary):
            return {
                "querysource": {
                    "@id": get_querysource_url(self.field, self.context, self.request)
                }
            }

        # Unamed ISource or vocabulary - render link addressing it via field
        #
        # Even though the URL will point to the @sources endpoint, we also
        # list it under the 'vocabulary' key, because the semantics for an
        # API consumer are exactly the same: A GET to that URL will enumerate
        # terms, and will support batching and filtering by title/token.
        result = {
            "vocabulary": {
                "@id": get_source_url(self.field, self.context, self.request)
            }
        }

        # Optionally inline choices for unnamed sources
        # (this is for BBB, and may eventually be deprecated)
        if hasattr(vocabulary, "__iter__") and self.should_render_choices:
            # choices and enumNames are v5 proposals, for now we implement both
            choices = []
            enum = []
            enum_names = []

            for term in vocabulary:
                if term.title:
                    title = translate(term.title, context=self.request)
                else:
                    title = None
                choices.append((term.token, title))
                enum.append(term.token)
                enum_names.append(title)

            result.update({"enum": enum, "enumNames": enum_names, "choices": choices})

        return result


@adapter(IObject, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ObjectJsonSchemaProvider(DefaultJsonSchemaProvider):

    prefix = ""

    def get_type(self):
        return "object"

    def get_factory(self):
        if self.field.schema.__name__ == "INamedBlobImage":
            return "Image"
        else:
            return "File"

    def get_properties(self):
        if self.prefix:
            prefix = ".".join([self.prefix, self.field.__name__])
        else:
            prefix = self.field.__name__

        context = self.context
        request = self.request
        fieldsets = get_fieldsets(context, request, self.field.schema)
        return get_jsonschema_properties(context, request, fieldsets, prefix)

    def additional(self):
        info = super(ObjectJsonSchemaProvider, self).additional()
        info["properties"] = self.get_properties()
        return info


@adapter(IDict, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DictJsonSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "dict"

    def additional(self):
        info = {}
        key_type = getMultiAdapter(
            (self.field.key_type, self.context, self.request), IJsonSchemaProvider
        )
        info["key_type"] = {
            "schema": key_type.get_schema(),
            "additional": key_type.additional(),
        }
        value_type = getMultiAdapter(
            (self.field.key_type, self.context, self.request), IJsonSchemaProvider
        )
        info["value_type"] = {
            "schema": value_type.get_schema(),
            "additional": value_type.additional(),
        }
        return info


@adapter(IRichText, Interface, Interface)
@implementer(IJsonSchemaProvider)
class RichTextJsonSchemaProvider(DefaultJsonSchemaProvider):

    prefix = ""

    def get_type(self):
        return "string"

    def get_widget(self):
        return "richtext"

    def get_factory(self):
        return "Rich Text"


@adapter(IDate, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DateJsonSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "string"

    def additional(self):
        info = {}
        if self.field.min is not None:
            info["minimum"] = self.field.min

        if self.field.max is not None:
            info["maximum"] = self.field.max

        return info

    def get_widget(self):
        return "date"

    def get_factory(self):
        return "Date"


@adapter(IDatetime, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DatetimeJsonSchemaProvider(DateJsonSchemaProvider):
    def get_widget(self):
        return "datetime"

    def get_factory(self):
        return "Date/Time"


@adapter(ITuple, Interface, Interface)
@implementer(IJsonSchemaProvider)
class SubjectsFieldJsonSchemaProvider(ChoiceJsonSchemaProvider):
    pass


@adapter(IJSONField, Interface, Interface)
@implementer(IJsonSchemaProvider)
class JSONFieldSchemaProvider(DefaultJsonSchemaProvider):
    def get_type(self):
        return "dict"

    def get_widget(self):
        return "json"

    def get_factory(self):
        return "JSONField"
