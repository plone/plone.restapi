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
from z3c.relationfield.relation import RelationValue
from zExceptions import BadRequest
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
from zope.schema.interfaces import ValidationError


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
        try:
            return IFromUnicode(self.field).fromUnicode(value)
        except ValidationError as e:
            raise BadRequest(e.doc())


@implementer(IFieldDeserializer)
@adapter(IDatetime, IDexterityContent, IBrowserRequest)
class DatetimeFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        try:
            # Parse ISO 8601 string with Zope's DateTime module
            # and convert to a timezone naive datetime in local time
            return DateTime(value).toZone(DateTime().localZone()).asdatetime(
            ).replace(tzinfo=None)
        except (SyntaxError, DateTimeError) as e:
            raise BadRequest(e.message)


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

        try:
            return self.field._type(value)
        except TypeError as e:
            raise BadRequest(e.message)


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
        return new_value


@implementer(IFieldDeserializer)
@adapter(ITime, IDexterityContent, IBrowserRequest)
class TimeFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        try:
            # Parse ISO 8601 string with Zope's DateTime module
            # and convert to a timezone naive time in local time
            return DateTime(u'2000-01-01T' + value).toZone(DateTime(
            ).localZone()).asdatetime().replace(tzinfo=None).time()
        except (SyntaxError, DateTimeError) as e:
            raise BadRequest(e.message)


@implementer(IFieldDeserializer)
@adapter(ITimedelta, IDexterityContent, IBrowserRequest)
class TimedeltaFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        try:
            return timedelta(seconds=value)
        except TypeError as e:
            raise BadRequest(e.message)


@implementer(IFieldDeserializer)
@adapter(INamedField, IDexterityContent, IBrowserRequest)
class NamedFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        content_type = 'application/octet-stream'
        filename = None
        if isinstance(value, dict):
            content_type = value.get(u'content-type', content_type)
            filename = value.get(u'filename', filename)
            if u'encoding' in value:
                data = value.get('data', '').decode(value[u'encoding'])
            else:
                data = value.get('data', '')
        else:
            data = value
        return self.field._type(
            data=data, contentType=content_type, filename=filename)


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
        return RichTextValue(
            raw=data,
            mimeType=content_type,
            outputMimeType=self.field.output_mime_type,
            encoding=encoding,
        )


@implementer(IFieldDeserializer)
@adapter(IRelationChoice, IDexterityContent, IBrowserRequest)
class RelationChoiceFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        intids = queryUtility(IIntIds)
        # Resolve by intid
        if isinstance(value, int):
            to_obj = intids.queryObject(value)
            if to_obj:
                return RelationValue(value)
        elif isinstance(value, basestring):
            portal = getMultiAdapter((self.context, self.request),
                                     name='plone_portal_state').portal()
            portal_url = portal.absolute_url()
            if value.startswith(portal_url):
                # Resolve by URL
                to_obj = portal.restrictedTraverse(
                    value[len(portal_url) + 1:].encode('utf8'), None)
                to_id = intids.queryId(to_obj)
            elif value.startswith('/'):
                # Resolve by path
                to_obj = portal.restrictedTraverse(
                    value.encode('utf8').lstrip('/'), None)
                to_id = intids.queryId(to_obj)
            else:
                # Resolve by UID
                catalog = getToolByName(self.context, 'portal_catalog')
                brain = catalog(UID=value)
                if brain:
                    to_id = intids.queryId(brain[0].getObject())

            if to_id:
                return RelationValue(to_id)
