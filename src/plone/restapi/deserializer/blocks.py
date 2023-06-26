from collections import deque
from copy import deepcopy
from plone import api
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.behaviors import IBlocks
from plone.restapi.blocks import iter_block_transform_handlers, visit_blocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.deserializer.utils import path2uid
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IFieldDeserializer
from plone.schema import IJSONField
from zope.component import adapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest

import os


def iterate_children(value):
    """iterate_children.

    :param value:
    """
    queue = deque(value)
    while queue:
        child = queue.pop()
        yield child
        if child.get("children"):
            queue.extend(child["children"] or [])


@implementer(IFieldDeserializer)
@adapter(IJSONField, IBlocks, IBrowserRequest)
class BlocksJSONFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        value = super().__call__(value)
        if self.field.getName() == "blocks":
            for block in visit_blocks(self.context, value):
                new_block = block.copy()
                for handler in iter_block_transform_handlers(
                    self.context, block, IBlockFieldDeserializationTransformer
                ):
                    new_block = handler(new_block)
                block.clear()
                block.update(new_block)
        return value


class ResolveUIDDeserializerBase:
    """The "url" smart block field.

    This is a generic handler. In all blocks, it converts any "url"
    field from using resolveuid to an "absolute" URL
    """

    order = 1
    block_type = None
    fields = ["url", "href"]
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # Convert absolute links to resolveuid
        return self._process_data(block)

    def _process_data(self, data, field=None):
        if isinstance(data, str) and field in self.fields:
            return path2uid(context=self.context, link=data)
        if isinstance(data, list):
            return [self._process_data(data=value, field=field) for value in data]
        if isinstance(data, dict):
            if data.get("@type", None) == "URL" and data.get("value", None):
                data["value"] = path2uid(context=self.context, link=data["value"])
            elif data.get("@id", None):
                data = deepcopy(data)
                data["@id"] = path2uid(context=self.context, link=data["@id"])
            data.pop("image_scales", None)
            return {
                field: self._process_data(data=value, field=field)
                for field, value in data.items()
            }
        return data


class TextBlockDeserializerBase:
    order = 100
    block_type = "text"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # Convert absolute links to resolveuid
        #   http://localhost:55001/plone/link-target
        #   ->
        #   ../resolveuid/023c61b44e194652804d05a15dc126f4
        entity_map = block.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                href = entity.get("data", {}).get("url", "")
                entity["data"]["url"] = path2uid(context=self.context, link=href)
        return block


class HTMLBlockDeserializerBase:
    order = 100
    block_type = "html"
    disabled = os.environ.get("disable_transform_html", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        portal_transforms = api.portal.get_tool(name="portal_transforms")
        raw_html = block.get("html", "")
        data = portal_transforms.convertTo(
            "text/x-html-safe", raw_html, mimetype="text/html"
        )
        html = data.getData()
        block["html"] = html

        return block


class ImageBlockDeserializerBase:
    order = 100
    block_type = "image"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        url = block.get("url", "")
        block["url"] = path2uid(context=self.context, link=url)
        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class ResolveUIDDeserializer(ResolveUIDDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class ResolveUIDDeserializerRoot(ResolveUIDDeserializerBase):
    """Deserializer for site root"""


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class TextBlockDeserializer(TextBlockDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class TextBlockDeserializerRoot(TextBlockDeserializerBase):
    """Deserializer for site root"""


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class HTMLBlockDeserializer(HTMLBlockDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class HTMLBlockDeserializerRoot(HTMLBlockDeserializerBase):
    """Deserializer for site root"""


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class ImageBlockDeserializer(ImageBlockDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class ImageBlockDeserializerRoot(ImageBlockDeserializerBase):
    """Deserializer for site root"""


def transform_links(context, value, transformer):
    """Convert absolute links to resolveuid
    http://localhost:55001/plone/link-target
    ->
    ../resolveuid/023c61b44e194652804d05a15dc126f4"""
    data = value.get("data", {})
    if data.get("link", {}).get("internal", {}).get("internal_link"):
        internal_link = data["link"]["internal"]["internal_link"]
        for link in internal_link:
            link["@id"] = transformer(context, link["@id"])


class SlateBlockTransformer:
    """SlateBlockTransformer."""

    field = "value"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        value = (block or {}).get(self.field, [])
        children = iterate_children(value or [])

        for child in children:
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, f"handle_{node_type}", None)
                if handler:
                    handler(child)

        return block


class SlateBlockDeserializerBase(SlateBlockTransformer):
    """SlateBlockDeserializerBase."""

    order = 100
    block_type = "slate"
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def handle_a(self, child):
        transform_links(self.context, child, transformer=path2uid)

    def handle_link(self, child):
        if child.get("data", {}).get("url"):
            child["data"]["url"] = path2uid(self.context, child["data"]["url"])


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializer(SlateBlockDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateBlockDeserializerRoot(SlateBlockDeserializerBase):
    """Deserializer for site root"""


class SlateTableBlockTransformer(SlateBlockTransformer):
    def __call__(self, block):
        rows = block.get("table", {}).get("rows", [])
        for row in rows:
            cells = row.get("cells", [])

            for cell in cells:
                cellvalue = cell.get("value", [])
                children = iterate_children(cellvalue or [])
                for child in children:
                    node_type = child.get("type")
                    if node_type:
                        handler = getattr(self, f"handle_{node_type}", None)
                        if handler:
                            handler(child)

        return block


class SlateTableBlockDeserializerBase(
    SlateTableBlockTransformer, SlateBlockDeserializerBase
):
    """SlateTableBlockDeserializerBase."""

    order = 100
    block_type = "slateTable"


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateTableBlockDeserializer(SlateTableBlockDeserializerBase):
    """Deserializer for content-types that implements IBlocks behavior"""


@adapter(IPloneSiteRoot, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class SlateTableBlockDeserializerRoot(SlateTableBlockDeserializerBase):
    """Deserializer for site root"""
