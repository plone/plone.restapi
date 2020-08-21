# -*- coding: utf-8 -*-
from plone.outputfilters.browser.resolveuid import uuidToObject
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.schema import IJSONField
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.component import subscribers
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import copy
import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


def uid_to_url(path):
    if not path:
        return ""
    match = RESOLVEUID_RE.match(path)
    if match is None:
        return path

    uid, suffix = match.groups()
    href = uuidToURL(uid)
    if href is None:
        return path
    if suffix:
        href += "/" + suffix
    else:
        target_object = uuidToObject(uid)
        if target_object:
            adapter = queryMultiAdapter(
                (target_object, target_object.REQUEST), IObjectPrimaryFieldTarget
            )
            if adapter and adapter():
                href = adapter()
    return href


@adapter(IJSONField, IBlocks, Interface)
@implementer(IFieldSerializer)
class BlocksJSONFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        value = copy.deepcopy(self.get_value())

        if self.field.getName() == "blocks":
            for id, block_value in value.items():
                block_type = block_value.get("@type", "")
                handlers = []
                for h in subscribers(
                    (self.context, self.request), IBlockFieldSerializationTransformer
                ):
                    if h.block_type == block_type or h.block_type is None:
                        handlers.append(h)

                for handler in sorted(handlers, key=lambda h: h.order):
                    block_value = handler(block_value)

                value[id] = block_value

        return json_compatible(value)


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class ResolveUIDSerializer(object):
    order = 1
    block_type = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        for field in ["url", "href"]:
            if field in value.keys():
                value[field] = uid_to_url(value.get(field, ""))
        return value


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class TextBlockSerializer(object):
    order = 100
    block_type = "text"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        # Resolve UID links
        entity_map = value.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") != "LINK":
                continue
            href = entity.get("data", {}).get("href", "")
            entity["data"]["href"] = uid_to_url(href)
        return value
