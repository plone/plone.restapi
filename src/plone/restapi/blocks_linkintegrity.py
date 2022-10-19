# -*- coding: utf-8 -*-
from plone.app.linkintegrity.interfaces import IRetriever
from plone.app.linkintegrity.retriever import DXGeneral
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.blocks import iterate_children
from plone.restapi.interfaces import IBlockFieldLinkIntegrityRetriever
from zope.component import adapter
from zope.component import subscribers
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


@implementer(IRetriever)
@adapter(IBlocks)
class BlocksRetriever(DXGeneral):
    """General retriever for Blocks enabled contents."""

    def retrieveLinks(self):
        """Finds all links from the object and return them."""
        links = set()
        blocks = getattr(self.context, "blocks", {})
        for block in blocks.values():
            block_type = block.get("@type", None)
            handlers = []
            for h in subscribers(
                (self.context, self.context.REQUEST),
                IBlockFieldLinkIntegrityRetriever,
            ):
                if h.block_type == block_type or h.block_type is None:
                    handlers.append(h)
            for handler in sorted(handlers, key=lambda h: h.order):
                links |= set(handler(block))

        return links


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class TextBlockLinksRetriever(object):
    order = 100
    block_type = "text"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        """
        Returns a list of internal links
        """
        links = []
        entity_map = block.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                for attr in ["href", "url"]:
                    relation = entity.get("data", {}).get(attr, "")
                    if relation and "resolveuid" in relation and relation not in links:
                        links.append(relation)
        return links


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class SlateBlockLinksRetriever:

    order = 100
    block_type = "slate"
    field = "value"

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.links = []

    def __call__(self, block):
        value = (block or {}).get(self.field, [])
        children = iterate_children(value or [])

        for child in children:
            node_type = child.get("type")
            if node_type:
                handler = getattr(self, f"handle_{node_type}", None)
                if handler:
                    self.links.append(handler(child))

        return self.links

    def handle_a(self, child):
        data = child.get("data", {})
        if data.get("link", {}).get("internal", {}).get("internal_link"):
            internal_link = data["link"]["internal"]["internal_link"]
            if len(internal_link) > 0:
                return internal_link[0]["@id"]

    def handle_link(self, child):
        if child.get("data", {}).get("url"):
            return child["data"]["url"]


@adapter(IBlocks, IBrowserRequest)
@implementer(IBlockFieldLinkIntegrityRetriever)
class GenericBlockLinksRetriever(object):
    order = 1
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        """
        Returns a list of internal links
        """
        links = []
        for field in ["url", "href"]:
            value = block.get(field, "")
            if value and "resolveuid" in value:
                links.append(value)
        return links
