# -*- coding: utf-8 -*-
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from Products.CMFCore.utils import getToolByName
from datetime import timedelta
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedField
from plone.restapi.interfaces import IFieldDeserializer
from z3c.relationfield.interfaces import IRelationChoice
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ITime
from zope.schema.interfaces import ITimedelta


@implementer(IFieldDeserializer)
@adapter(IField, IDexterityContent, IBrowserRequest)
class DefaultFieldDeserializer(object):

    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __call__(self, value):
        if not isinstance(value, unicode):
            return value
        return IFromUnicode(self.field).fromUnicode(value)


@implementer(IFieldDeserializer)
@adapter(IDatetime, IDexterityContent, IBrowserRequest)
class DatetimeFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        try:
            # Parse ISO 8601 string with Zope's DateTime module
            # and convert to a timezone naive datetime in local time
            value = DateTime(value).toZone(DateTime().localZone()).asdatetime(
            ).replace(tzinfo=None)
        except (SyntaxError, DateTimeError) as e:
            raise ValueError(e.message)

        self.field.validate(value)
        return value


@implementer(IFieldDeserializer)
@adapter(ICollection, IDexterityContent, IBrowserRequest)
class CollectionFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        if not isinstance(value, list):
            value = [value]

        if IField.providedBy(self.field.value_type):
            deserializer = getMultiAdapter(
                (self.field.value_type, self.context, self.request),
                IFieldDeserializer)

            for i, v in enumerate(value):
                value[i] = deserializer(v)

        value = self.field._type(value)
        self.field.validate(value)

        return value


@implementer(IFieldDeserializer)
@adapter(IDict, IDexterityContent, IBrowserRequest)
class DictFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        kdeserializer = lambda k: k
        vdeserializer = lambda v: v
        if IField.providedBy(self.field.key_type):
            kdeserializer = getMultiAdapter(
                (self.field.key_type, self.context, self.request),
                IFieldDeserializer)
        if IField.providedBy(self.field.value_type):
            vdeserializer = getMultiAdapter(
                (self.field.value_type, self.context, self.request),
                IFieldDeserializer)

        new_value = {}
        for k, v in value.items():
            new_value[kdeserializer(k)] = vdeserializer(v)

        self.field.validate(new_value)
        return new_value


@implementer(IFieldDeserializer)
@adapter(ITime, IDexterityContent, IBrowserRequest)
class TimeFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        try:
            # Create an ISO 8601 datetime string and parse it with Zope's
            # DateTime module and then convert it to a timezone naive time
            # in local time
            value = DateTime(u'2000-01-01T' + value).toZone(DateTime(
            ).localZone()).asdatetime().replace(tzinfo=None).time()
        except (SyntaxError, DateTimeError):
            raise ValueError(u'Invalid time: {}'.format(value))

        self.field.validate(value)
        return value


@implementer(IFieldDeserializer)
@adapter(ITimedelta, IDexterityContent, IBrowserRequest)
class TimedeltaFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        try:
            value = timedelta(seconds=value)
        except TypeError as e:
            raise ValueError(e.message)

        self.field.validate(value)
        return value


@implementer(IFieldDeserializer)
@adapter(INamedField, IDexterityContent, IBrowserRequest)
class NamedFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        content_type = 'application/octet-stream'
        filename = None
        if isinstance(value, dict):
            content_type = value.get(u'content-type', content_type).encode(
                'utf8')
            filename = value.get(u'filename', filename)
            if u'encoding' in value:
                data = value.get('data', '').decode(value[u'encoding'])
            else:
                data = value.get('data', '')
        else:
            data = value

        value = self.field._type(
            data=data, contentType=content_type, filename=filename)
        self.field.validate(value)
        return value


@implementer(IFieldDeserializer)
@adapter(IRichText, IDexterityContent, IBrowserRequest)
class RichTextFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        content_type = self.field.default_mime_type
        encoding = 'utf8'
        if isinstance(value, dict):
            content_type = value.get(u'content-type', content_type)
            encoding = value.get(u'encoding', encoding)
            data = value.get(u'data', u'')
        else:
            data = value

        value = RichTextValue(
            raw=data,
            mimeType=content_type,
            outputMimeType=self.field.output_mime_type,
            encoding=encoding,
        )
        self.field.validate(value)
        return value


@implementer(IFieldDeserializer)
@adapter(IRelationChoice, IDexterityContent, IBrowserRequest)
class RelationChoiceFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        obj = None

        if isinstance(value, int):
            # Resolve by intid
            intids = queryUtility(IIntIds)
            obj = intids.queryObject(value)
        elif isinstance(value, basestring):
            portal = getMultiAdapter((self.context, self.request),
                                     name='plone_portal_state').portal()
            portal_url = portal.absolute_url()
            if value.startswith(portal_url):
                # Resolve by URL
                obj = portal.restrictedTraverse(
                    value[len(portal_url) + 1:].encode('utf8'), None)
            elif value.startswith('/'):
                # Resolve by path
                obj = portal.restrictedTraverse(
                    value.encode('utf8').lstrip('/'), None)
            else:
                # Resolve by UID
                catalog = getToolByName(self.context, 'portal_catalog')
                brain = catalog(UID=value)
                if brain:
                    obj = brain[0].getObject()

        self.field.validate(obj)
        return obj
