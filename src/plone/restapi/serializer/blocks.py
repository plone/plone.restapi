from copy import deepcopy
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import SlateBlockTransformer
from plone.restapi.deserializer.blocks import transform_links
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.serializer.utils import uid_to_url
from plone.schema import IJSONField
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import copy
import os


@adapter(IJSONField, IBlocks, Interface)
@implementer(IFieldSerializer)
class BlocksJSONFieldSerializer(DefaultFieldSerializer):
    def _transform(self, blocks):
        for id, block_value in blocks.items():
            self.handle_subblocks(block_value)
            block_type = block_value.get("@type", "")
            handlers = []
            for h in subscribers(
                (self.context, self.request), IBlockFieldSerializationTransformer
            ):
                if h.block_type == block_type or h.block_type is None:
                    h.blockid = id
                    handlers.append(h)

            for handler in sorted(handlers, key=lambda h: h.order):
                block_value = handler(block_value)

            blocks[id] = block_value

        return blocks

    def handle_subblocks(self, block_value):
        if "data" in block_value:
            if isinstance(block_value["data"], dict):
                if "blocks" in block_value["data"]:
                    block_value["data"]["blocks"] = self._transform(
                        block_value["data"]["blocks"]
                    )

        if "blocks" in block_value:
            block_value["blocks"] = self._transform(block_value["blocks"])

    def __call__(self):
        value = copy.deepcopy(self.get_value())

        if self.field.getName() == "blocks":
            for id, block_value in value.items():
                self.handle_subblocks(block_value)
                block_type = block_value.get("@type", "")
                handlers = []
                for h in subscribers(
                    (self.context, self.request), IBlockFieldSerializationTransformer
                ):
                    if h.block_type == block_type or h.block_type is None:
                        h.blockid = id
                        handlers.append(h)

                for handler in sorted(handlers, key=lambda h: h.order):
                    if not getattr(handler, "disabled", False):
                        block_value = handler(block_value)

                value[id] = block_value

        return json_compatible(value)


class ResolveUIDSerializerBase:
    order = 1
    block_type = None
    fields = ["url", "href"]
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        for field in self.fields:
            if field in value.keys():
                link = value.get(field, "")
                if isinstance(link, str):
                    value[field] = uid_to_url(link)
                elif isinstance(link, list):
                    if len(link) > 0 and isinstance(link[0], dict) and "@id" in link[0]:
                        result = []
                        for item in link:
                            item_clone = deepcopy(item)
                            item_clone["@id"] = uid_to_url(item_clone["@id"])
                            result.append(item_clone)

                        value[field] = result
                    elif len(link) > 0 and isinstance(link[0], str):
                        value[field] = [uid_to_url(item) for item in link]
        return value


class TextBlockSerializerBase:
    order = 100
    block_type = "text"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        # Resolve UID links:
        #   ../resolveuid/023c61b44e194652804d05a15dc126f4
        #   ->
        #   http://localhost:55001/plone/link-target
        entity_map = value.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                url = entity.get("data", {}).get("url", "")
                entity["data"]["url"] = uid_to_url(url)
        return value


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ResolveUIDSerializer(ResolveUIDSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class ResolveUIDSerializerRoot(ResolveUIDSerializerBase):
    """Serializer for site root"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class TextBlockSerializer(TextBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class TextBlockSerializerRoot(TextBlockSerializerBase):
    """Serializer for site root"""


class SlateBlockSerializerBase(SlateBlockTransformer):
    """SlateBlockSerializerBase."""

    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def _uid_to_url(self, context, path):
        return uid_to_url(path)

    def handle_a(self, child):
        transform_links(self.context, child, transformer=self._uid_to_url)

    def handle_link(self, child):
        if child.get("data", {}).get("url"):
            child["data"]["url"] = uid_to_url(child["data"]["url"])


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateBlockSerializer(SlateBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateBlockSerializerRoot(SlateBlockSerializerBase):
    """Serializer for site root"""
