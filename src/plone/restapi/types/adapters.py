# -*- coding: utf-8 -*-
"""JsonSchema providers."""
from plone.autoform.interfaces import WIDGETS_KEY

from plone.app.textfield.interfaces import IRichText
from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from plone.schema import IJSONField
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface
from zope.schema.interfaces import IASCII
from zope.schema.interfaces import IASCIILine
from zope.schema.interfaces import IBool
from zope.schema.interfaces import IBytes
from zope.schema.interfaces import IChoice
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDate
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IDecimal
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFloat
from zope.schema.interfaces import IInt
from zope.schema.interfaces import IList
from zope.schema.interfaces import IObject
from zope.schema.interfaces import ISet
from zope.schema.interfaces import IText
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import ITuple

from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import get_fieldsets, get_tagged_values
from plone.restapi.types.utils import get_jsonschema_properties
from plone.restapi.types.utils import get_jsonschema_for_vocab


@adapter(IField, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DefaultJsonSchemaProvider(object):

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def additional(self):
        """Additional info for field."""
        return {}

    def get_title(self):
        return translate(self.field.title, context=self.request)

    def get_description(self):
        if self.field.description is None:
            return u''

        return translate(self.field.description, context=self.request)

    def get_schema(self):
        """Get jsonschema for field.

        You should override `additional` method to provide more properties
        about the field."""
        schema = {
            'type': self.get_type(),
            'title': self.get_title(),
            'description': self.get_description(),
        }

        widget = self.get_widget()
        if widget:
            schema['widget'] = widget

        if self.field.default is not None:
            schema['default'] = self.field.default

        schema.update(self.additional())
        return schema

    def get_type(self):
        raise NotImplementedError

    def get_widget(self):
        return None


@adapter(IBytes, Interface, Interface)
@implementer(IJsonSchemaProvider)
class BytesLineJsonSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'string'


@adapter(ITextLine, Interface, Interface)
@implementer(IJsonSchemaProvider)
class TextLineJsonSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'string'


@adapter(IText, Interface, Interface)
@implementer(IJsonSchemaProvider)
class TextJsonSchemaProvider(TextLineJsonSchemaProvider):

    def additional(self):
        info = {}
        if self.field.min_length is not None:
            info['minLength'] = self.field.min_length

        if self.field.max_length is not None:
            info['maxLength'] = self.field.max_length

        return info

    def get_widget(self):
        return 'textarea'


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
        return 'number'

    def additional(self):
        info = {}
        if self.field.min is not None:
            info['minimum'] = self.field.min

        if self.field.max is not None:
            info['maximum'] = self.field.max

        return info


@adapter(IDecimal, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DecimalJsonSchemaProvider(FloatJsonSchemaProvider):

    pass


@adapter(IInt, Interface, Interface)
@implementer(IJsonSchemaProvider)
class IntegerJsonSchemaProvider(FloatJsonSchemaProvider):

    def get_type(self):
        return 'integer'


@adapter(IBool, Interface, Interface)
@implementer(IJsonSchemaProvider)
class BoolJsonSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'boolean'


@adapter(ICollection, Interface, Interface)
@implementer(IJsonSchemaProvider)
class CollectionJsonSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'array'

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request),
            IJsonSchemaProvider)

        return value_type_adapter.get_schema()

    def additional(self):
        info = {}
        info['additionalItems'] = True
        if self.field.min_length:
            info['minItems'] = self.field.min_length

        if self.field.max_length:
            info['maxItems'] = self.field.max_length

        info['items'] = self.get_items()

        return info


@adapter(IList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ListJsonSchemaProvider(CollectionJsonSchemaProvider):

    def additional(self):
        info = super(ListJsonSchemaProvider, self).additional()
        if IChoice.providedBy(self.field.value_type):
            info['uniqueItems'] = True
        else:
            info['uniqueItems'] = False

        return info


@adapter(ISet, Interface, Interface)
@implementer(IJsonSchemaProvider)
class SetJsonSchemaProvider(CollectionJsonSchemaProvider):

    def additional(self):
        info = super(SetJsonSchemaProvider, self).additional()
        info['uniqueItems'] = True
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
        return 'string'

    def additional(self):
        if not self.should_render_choices:
            return {}

        vocabulary = None
        if getattr(self.field, 'vocabulary', None):
            vocabulary = self.field.vocabulary
        vocab_name = getattr(self.field, 'vocabularyName', None)
        if not vocab_name and not vocabulary:
            tagged = get_tagged_values([self.field.interface], WIDGETS_KEY)
            tagged_field_values = tagged.get(self.field.getName(), {})
            vocab_name = tagged_field_values.get('vocabulary', None)

        return get_jsonschema_for_vocab(
            self.context, self.request, vocab_name, vocabulary)


@adapter(IObject, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ObjectJsonSchemaProvider(DefaultJsonSchemaProvider):

    prefix = ''

    def get_type(self):
        return 'object'

    def get_properties(self):
        if self.prefix:
            prefix = '.'.join([self.prefix, self.field.__name__])
        else:
            prefix = self.field.__name__

        context = self.context
        request = self.request
        fieldsets = get_fieldsets(context, request, self.field.schema)
        return get_jsonschema_properties(context, request, fieldsets, prefix)

    def additional(self):
        info = super(ObjectJsonSchemaProvider, self).additional()
        info['properties'] = self.get_properties()
        return info


@adapter(IDict, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DictJsonSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'dict'

    def additional(self):
        info = {}
        key_type = getMultiAdapter(
            (self.field.key_type, self.context, self.request),
            IJsonSchemaProvider
        )
        info['key_type'] = {
            'schema': key_type.get_schema(),
            'additional': key_type.additional(),
        }
        value_type = getMultiAdapter(
            (self.field.key_type, self.context, self.request),
            IJsonSchemaProvider
        )
        info['value_type'] = {
            'schema': value_type.get_schema(),
            'additional': value_type.additional(),
        }
        return info


@adapter(IRichText, Interface, Interface)
@implementer(IJsonSchemaProvider)
class RichTextJsonSchemaProvider(DefaultJsonSchemaProvider):

    prefix = ''

    def get_type(self):
        return 'string'

    def get_widget(self):
        return 'richtext'


@adapter(IDate, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DateJsonSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'string'

    def additional(self):
        info = {}
        if self.field.min is not None:
            info['minimum'] = self.field.min

        if self.field.max is not None:
            info['maximum'] = self.field.max

        return info

    def get_widget(self):
        return 'date'


@adapter(IDatetime, Interface, Interface)
@implementer(IJsonSchemaProvider)
class DatetimeJsonSchemaProvider(DateJsonSchemaProvider):

    def get_widget(self):
        return 'datetime'


@adapter(ITuple, Interface, Interface)
@implementer(IJsonSchemaProvider)
class SubjectsFieldJsonSchemaProvider(ChoiceJsonSchemaProvider):
    pass


@adapter(IJSONField, Interface, Interface)
@implementer(IJsonSchemaProvider)
class JSONFieldSchemaProvider(DefaultJsonSchemaProvider):

    def get_type(self):
        return 'dict'

    def get_widget(self):
        return 'json'


QUERY_FIELD_WIDGETS = {
    'DateRangeWidget': 'daterange',
    'RelativeDateWidget': 'relativedate',
    'ReferenceWidget': 'reference',
}


@adapter(IList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class QueryFieldJsonSchemaProvider(ListJsonSchemaProvider):

    def get_items(self):
        result = super(QueryFieldJsonSchemaProvider, self).get_items()
        criteria_schemas = []
        for fname, field, opname, operation in self._iter_criteria():
            value_schema = {
                "type": "string",
            }
            vocab_name = field.get('vocabulary')
            if vocab_name:
                value_schema.update(
                    get_jsonschema_for_vocab(
                        self.context, self.request, vocab_name))
            widget = operation.get('widget')
            if widget == 'DateWidget':
                value_schema['type'] = 'datetime'
            widget = QUERY_FIELD_WIDGETS.get(widget)
            if widget:
                value_schema['widget'] = widget

            criteria_schemas.append({
                "properties": {
                    "i": {
                        "const": fname,
                        "title": field['title'],
                        "description": field['description'],
                    },
                    "o": {
                        "const": opname,
                        "title": operation['title'],
                        "description": operation['description'],
                    },
                    "v": value_schema,
                }
            })
        result['anyOf'] = criteria_schemas
        return result

    def _iter_criteria(self):
        registry = getUtility(IRegistry)
        reader = getMultiAdapter(
            (registry, self.request), IQuerystringRegistryReader)
        values = reader.parseRegistry()
        for fname, field in values.get(reader.prefix + '.field').items():
            for opname in field['operations']:
                operation = values.get(opname)
                if opname.startswith('plone.app.querystring.operation.'):
                    opname = opname[
                        len('plone.app.querystring.operation') + 1:]
                yield fname, field, opname, operation
