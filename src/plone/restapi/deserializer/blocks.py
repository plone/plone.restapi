from Acquisition import aq_parent
from collections import deque
from copy import deepcopy
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IFieldDeserializer
from plone.schema import IJSONField
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import subscribers
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


def path2uid(context, link):
    # unrestrictedTraverse requires a string on py3. see:
    # https://github.com/zopefoundation/Zope/issues/674
    if not link:
        return ""
    portal = getMultiAdapter(
        (context, context.REQUEST), name="plone_portal_state"
    ).portal()
    portal_url = portal.portal_url()
    portal_path = "/".join(portal.getPhysicalPath())
    path = link
    context_url = context.absolute_url()
    relative_up = len(context_url.split("/")) - len(portal_url.split("/"))
    if path.startswith(portal_url):
        path = path[len(portal_url) + 1 :]
    if not path.startswith(portal_path):
        path = "{portal_path}/{path}".format(
            portal_path=portal_path, path=path.lstrip("/")
        )
    obj = portal.unrestrictedTraverse(path, None)
    if obj is None or obj == portal:
        return link
    segments = path.split("/")
    suffix = ""
    while not IUUIDAware.providedBy(obj):
        obj = aq_parent(obj)
        suffix += "/" + segments.pop()
    href = relative_up * "../" + "resolveuid/" + IUUID(obj)
    if suffix:
        href += suffix
    return href


@implementer(IFieldDeserializer)
@adapter(IJSONField, IBlocks, IBrowserRequest)
class BlocksJSONFieldDeserializer(DefaultFieldDeserializer):
    def _transform(self, blocks):
        for id, block_value in blocks.items():
            self.handle_subblocks(block_value)
            block_type = block_value.get("@type", "")
            handlers = []
            for h in subscribers(
                (self.context, self.request), IBlockFieldDeserializationTransformer
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

    def __call__(self, value):
        value = super().__call__(value)

        if self.field.getName() == "blocks":
            for id, block_value in value.items():
                self.handle_subblocks(block_value)
                block_type = block_value.get("@type", "")

                handlers = []
                for h in subscribers(
                    (self.context, self.request),
                    IBlockFieldDeserializationTransformer,
                ):
                    if h.block_type == block_type or h.block_type is None:
                        h.blockid = id
                        handlers.append(h)

                for handler in sorted(handlers, key=lambda h: h.order):
                    if not getattr(handler, "disabled", False):
                        block_value = handler(block_value)

                value[id] = block_value

        return value


class ResolveUIDDeserializerBase:
    """The "url" smart block field.

    This is a generic handler. In all blocks, it converts any "url"
    field from using resolveuid to an "absolute" URL
    """

    order = 1
    block_type = None
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # Convert absolute links to resolveuid
        for field in ["url", "href"]:
            link = block.get(field, "")
            if link and isinstance(link, str):
                block[field] = path2uid(context=self.context, link=link)
            elif link and isinstance(link, list):
                # Detect if it has an object inside with an "@id" key (object_widget)
                if len(link) > 0 and isinstance(link[0], dict) and "@id" in link[0]:
                    result = []
                    for item in link:
                        item_clone = deepcopy(item)
                        item_clone["@id"] = path2uid(
                            context=self.context, link=item_clone["@id"]
                        )
                        result.append(item_clone)

                    block[field] = result
                elif len(link) > 0 and isinstance(link[0], str):
                    block[field] = [
                        path2uid(context=self.context, link=item) for item in link
                    ]
        return block


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
