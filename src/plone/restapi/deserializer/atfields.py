# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.services.content.tus import TUSUpload
from Products.Archetypes.interfaces import IBaseObject
from Products.Archetypes.interfaces.field import IField
from Products.Archetypes.interfaces.field import IFileField
from Products.Archetypes.interfaces.field import IReferenceField
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import pkg_resources

try:
    pkg_resources.get_distribution("plone.app.blob")
except pkg_resources.DistributionNotFound:
    HAS_BLOB = False
else:
    HAS_BLOB = True
    from plone.app.blob.interfaces import IBlobField


@implementer(IFieldDeserializer)
@adapter(IField, IBaseObject, IBrowserRequest)
class DefaultFieldDeserializer(object):
    def __init__(self, field, context, request):
        self.field = field
        self.context = context
        self.request = request

    def __call__(self, value):
        return value, {}


@implementer(IFieldDeserializer)
@adapter(IFileField, IBaseObject, IBrowserRequest)
class FileFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        kwargs = {}
        if isinstance(value, dict):
            if u"content-type" in value:
                kwargs[u"mimetype"] = value[u"content-type"].encode("utf8")
            if u"filename" in value:
                kwargs[u"filename"] = value[u"filename"].encode("utf8")
            if u"encoding" in value:
                value = value.get("data", "").decode(value[u"encoding"])
            else:
                value = value.get("data", "")
        elif isinstance(value, TUSUpload):
            metadata = value.metadata()
            if "content-type" in metadata:
                kwargs[u"mimetype"] = metadata["content-type"]
            if "filename" in metadata:
                kwargs[u"filename"] = metadata["filename"]
            value = value.open()

        return value, kwargs


if HAS_BLOB:

    @implementer(IFieldDeserializer)
    @adapter(IBlobField, IBaseObject, IBrowserRequest)
    class BlobFieldDeserializer(FileFieldDeserializer):
        pass


@implementer(IFieldDeserializer)
@adapter(IReferenceField, IBaseObject, IBrowserRequest)
class ReferenceFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()

        if not isinstance(value, list):
            value = [value]

        for i, v in enumerate(value):
            # Resolve references given by URL
            if v.startswith(portal_url):
                path = v[len(portal_url) + 1 :].encode("utf8")
                value[i] = portal.unrestrictedTraverse(path, None)

        return value, {}
