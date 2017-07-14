# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.interface import implementer

from plone.restapi.deserializer.mixins import OrderingMixin
from zope.publisher.interfaces import IRequest


@implementer(IDeserializeFromJson)
@adapter(IPloneSiteRoot, IRequest)
class DeserializeSiteRootFromJson(OrderingMixin, object):
    """JSON deserializer for the Plone site root
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, validate_all=False):
        # Currently we only do layout and ordering, as the plone site root
        # has no schema or something like that.
        data = json_body(self.request)

        if 'layout' in data:
            layout = data['layout']
            self.context.setLayout(layout)

        # OrderingMixin
        if 'ordering' in data and 'subset_ids' not in data['ordering']:
            data['ordering']['subset_ids'] = self.context.contentIds()
        self.handle_ordering(data)

        return self.context
