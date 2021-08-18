from plone.restapi.deserializer import json_body
from plone.restapi.deserializer.mixins import OrderingMixin
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces import IRequest

import json


@implementer(IDeserializeFromJson)
@adapter(IPloneSiteRoot, IRequest)
class DeserializeSiteRootFromJson(OrderingMixin):
    """JSON deserializer for the Plone site root"""

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

        # Volto Blocks on the Plone Site root faker
        if "blocks" in data:
            value = data["blocks"]
            for id, block_value in value.items():
                block_type = block_value.get("@type", "")
                handlers = []
                for h in subscribers(
                    (self.context, self.request),
                    IBlockFieldDeserializationTransformer,
                ):
                    if h.block_type == block_type or h.block_type is None:
                        handlers.append(h)
                for handler in sorted(handlers, key=lambda h: h.order):
                    block_value = handler(block_value)
                value[id] = block_value
            if not getattr(self.context, "blocks", False):
                self.context.manage_addProperty(
                    "blocks", json.dumps(value), "string"
                )  # noqa
            else:
                self.context.manage_changeProperties(blocks=json.dumps(value))  # noqa

        if "blocks_layout" in data:
            if not getattr(self.context, "blocks_layout", False):
                self.context.manage_addProperty(
                    "blocks_layout", json.dumps(data["blocks_layout"]), "string"
                )  # noqa
            else:
                self.context.manage_changeProperties(
                    blocks_layout=json.dumps(data["blocks_layout"])
                )  # noqa

        if "title" in data:
            self.context.setTitle(data["title"])

        if "description" in data:
            self.context.manage_changeProperties(
                description=data["description"]
            )  # noqa

        return self.context
