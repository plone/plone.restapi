# -*- coding: utf-8 -*-
"""JsonSchema providers."""
from plone.app.textfield.interfaces import IRichText
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
from zope.schema.interfaces import IVocabularyFactory

from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.types.utils import get_jsonschema_properties


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
        # choices and enumNames are v5 proposals, for now we implement both
        choices = []
        enum = []
        enum_names = []
        if self.field.vocabularyName:
            vocabulary = getUtility(
                IVocabularyFactory,
                name=self.field.vocabularyName)(self.context)
        else:
            vocabulary = self.field.vocabulary

        if hasattr(vocabulary, '__iter__') and self.should_render_choices:
            for term in vocabulary:
                title = translate(term.title, context=self.request)
                choices.append((term.token, title))
                enum.append(term.token)
                enum_names.append(title)

            return {
                'enum': enum,
                'enumNames': enum_names,
                'choices': choices,
            }
        else:
            return {}


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
