# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import ICollection
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.interface import implementer


@implementer(ISerializeToJson)
@adapter(ICollection, Interface)
class SerializeCollectionToJson(SerializeToJson):

    def __call__(self):
        result = super(SerializeCollectionToJson, self).__call__()
        result['member'] = [
            getMultiAdapter((member, self.request), ISerializeToJsonSummary)()
            for member in self.context.results()
        ]
        return result
