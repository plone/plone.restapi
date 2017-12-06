# -*- coding: utf-8 -*-
from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from datetime import timedelta
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.interfaces import INamedField
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.services.content.tus import TUSUpload
from pytz import timezone
from pytz import utc
from z3c.form.interfaces import IDataManager
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema.interfaces import ICollection
from zope.schema.interfaces import IDatetime
from zope.schema.interfaces import IDict
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ITextLine
from zope.schema.interfaces import ITime
from zope.schema.interfaces import ITimedelta


@implementer(IFieldDeserializer)
@adapter(IField, IDexterityContent, IBrowserRequest)
class DefaultFieldDeserializer(object):

    def __init__(self, field, context, request):
        self.field = field
        if IField.providedBy(self.field):
            self.field = self.field.bind(context)
        self.context = context
        self.request = request

    def __call__(self, value):
        if not isinstance(value, unicode):
            return value
        return IFromUnicode(self.field).fromUnicode(value)


@implementer(IFieldDeserializer)
@adapter(ITextLine, IDexterityContent, IBrowserRequest)
class TextLineFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        if isinstance(value, unicode):
            value = IFromUnicode(self.field).fromUnicode(value)

        # Mimic what z3c.form does in it's BaseDataConverter.
        if isinstance(value, unicode):
            value = value.strip()
            if value == u'':
                value = self.field.missing_value

        self.field.validate(value)
        return value


@implementer(IFieldDeserializer)
@adapter(IDatetime, IDexterityContent, IBrowserRequest)
class DatetimeFieldDeserializer(DefaultFieldDeserializer):

    def __call__(self, value):
        # Datetime fields may contain timezone naive or timezone aware
        # objects. Unfortunately the zope.schema.Datetime field does not
        # contain any information if the field value should be timezone naive
        # or timezone aware. While some fields (start, end) store timezone
        # aware objects others (effective, expires) store timezone naive
        # objects.
        # We try to guess the correct deserialization from the current field
        # value.
        dm = queryMultiAdapter((self.context, self.field), IDataManager)
        current = dm.get()
        if current is not None:
            tzinfo = current.tzinfo
        else:
            tzinfo = None

        # This happens when a 'null' is posted for a non-required field.
        if value is None:
            self.field.validate(value)
            return

        # Parse ISO 8601 string with Zope's DateTime module
        try:
            dt = DateTime(value).asdatetime()
        except (SyntaxError, DateTimeError) as e:
            raise ValueError(e.message)

        # Convert to TZ aware in UTC
        if dt.tzinfo is not None:
            dt = dt.astimezone(utc)
        else:
            dt = utc.localize(dt)

        # Convert to local TZ aware or naive UTC
        if tzinfo is not None:
            tz = timezone(tzinfo.zone)
            value = tz.normalize(dt.astimezone(tz))
        else:
            value = utc.normalize(dt.astimezone(utc)).replace(tzinfo=None)

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
        if IField.providedBy(self.field.key_type):
            kdeserializer = getMultiAdapter(
                (self.field.key_type, self.context, self.request),
                IFieldDeserializer)
        else:
            def kdeserializer(k):
                return k

        if IField.providedBy(self.field.value_type):
            vdeserializer = getMultiAdapter(
                (self.field.value_type, self.context, self.request),
                IFieldDeserializer)
        else:
            def vdeserializer(v):
                return v

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
            if 'data' not in value:
                # We are probably pushing the contents of a previous GET
                # That contain the read representation of the file
                # with the 'download' key so we return the same stored file
                return getattr(self.field.context, self.field.__name__)

            content_type = value.get(u'content-type', content_type).encode(
                'utf8')
            filename = value.get(u'filename', filename)
            if u'encoding' in value:
                data = value.get('data', '').decode(value[u'encoding'])
            else:
                data = value.get('data', '')
        elif isinstance(value, TUSUpload):
            content_type = value.metadata().get(
                'content-type', content_type).encode('utf8')
            filename = value.metadata().get('filename', filename)
            data = value.open()
        else:
            data = value

        # Convert if we have data
        if data:
            value = self.field._type(
                data=data, contentType=content_type, filename=filename)
        else:
            value = None

        # Always validate to check for required fields
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
        elif isinstance(value, TUSUpload):
            content_type = value.metadata().get('content-type', content_type)
            with open(value.filepath, 'rb') as f:
                data = f.read().decode('utf8')
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
