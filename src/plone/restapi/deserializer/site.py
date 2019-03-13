# -*- coding: utf-8 -*-
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from zope.component import adapter
from zope.interface import implementer

from plone.restapi.deserializer.mixins import OrderingMixin
from zope.publisher.interfaces import IRequest

import json


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

        if "layout" in data:
            layout = data["layout"]
            self.context.setLayout(layout)

        # OrderingMixin
        if "ordering" in data and "subset_ids" not in data["ordering"]:
            data["ordering"]["subset_ids"] = self.context.contentIds()
        self.handle_ordering(data)

        # Volto Tiles on the Plone Site root faker
        if "tiles" in data:
            if not getattr(self.context, "tiles", False):
                self.context.manage_addProperty(
                    "tiles", json.dumps(data["tiles"]), "string"
                )  # noqa
            else:
                self.context.manage_changeProperties(
                    tiles=json.dumps(data["tiles"])
                )  # noqa

        if "tiles_layout" in data:
            if not getattr(self.context, "tiles_layout", False):
                self.context.manage_addProperty(
                    "tiles_layout", json.dumps(data["tiles_layout"]), "string"
                )  # noqa
            else:
                self.context.manage_changeProperties(
                    tiles_layout=json.dumps(data["tiles_layout"])
                )  # noqa

        if "title" in data:
            self.context.setTitle(data["title"])

        if "description" in data:
            self.context.manage_changeProperties(
                description=data["description"]
            )  # noqa

        return self.context
