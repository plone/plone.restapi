# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IBlockFieldDeserializationTransformer
from plone.restapi.interfaces import IFieldDeserializer
from plone.schema import IJSONField
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


def path2uid(context, path):
    # unrestrictedTraverse requires a string on py3. see:
    # https://github.com/zopefoundation/Zope/issues/674
    if not isinstance(path, str):
        path = path.decode("utf-8")
    obj = context.unrestrictedTraverse(path, None)
    if obj is None:
        return None, None
    segments = path.split("/")
    suffix = ""
    while not IUUIDAware.providedBy(obj):
        obj = aq_parent(obj)
        suffix += "/" + segments.pop()
    return IUUID(obj), suffix


@implementer(IFieldDeserializer)
@adapter(IJSONField, IBlocks, IBrowserRequest)
class BlocksJSONFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        value = super(BlocksJSONFieldDeserializer, self).__call__(value)

        if self.field.getName() == "blocks":

            for id, block_value in value.items():
                block_type = block_value.get("@type", "")

                handlers = [
                    h
                    for h in subscribers(
                        (self.context, self.request),
                        IBlockFieldDeserializationTransformer,
                    )
                    if h.block_type == block_type
                ]

                for handler in sorted(handlers, key=lambda h: h.order):
                    block_value = handler(block_value)

                value[id] = block_value

        return value


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class TextBlockDeserializer(object):
    order = 100
    block_type = "text"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        # Convert absolute links to resolveuid
        # Assumes in-place mutations

        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()
        context_url = self.context.absolute_url()
        relative_up = len(context_url.split("/")) - len(portal_url.split("/"))
        entity_map = block.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                href = entity.get("data", {}).get("url", "")
                before = href  # noqa
                if href and href.startswith(portal_url):
                    path = href[len(portal_url) + 1 :].encode("utf8")
                    uid, suffix = path2uid(portal, path)
                    if uid:
                        href = relative_up * "../" + "resolveuid/" + uid
                        if suffix:
                            href += suffix
                        entity["data"]["href"] = href
                        entity["data"]["url"] = href
                    print("DESERIALIZE " + before + " -> " + href)  # noqa

        return block


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class HTMLBlockDeserializer(object):
    order = 100
    block_type = "html"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):

        portal_transforms = api.portal.get_tool(name="portal_transforms")
        raw_html = value.get("html", "")
        data = portal_transforms.convertTo(
            "text/x-html-safe", raw_html, mimetype="text/html"
        )
        html = data.getData()
        value["html"] = html

        return value


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldDeserializationTransformer)
class ImageBlockDeserializer(object):
    order = 100
    block_type = "image"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()
        context_url = self.context.absolute_url()
        relative_up = len(context_url.split("/")) - len(portal_url.split("/"))

        href = value.get("url", "")

        if href and href.startswith(portal_url):
            path = href[len(portal_url) + 1 :].encode("utf8")
            uid, suffix = path2uid(portal, path)
            if uid:
                href = relative_up * "../" + "resolveuid/" + uid
                if suffix:
                    href += suffix

        value["url"] = href
        return value
