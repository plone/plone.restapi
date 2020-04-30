# -*- coding: utf-8 -*-
from plone.outputfilters.browser.resolveuid import uuidToObject
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IObjectPrimaryFieldTarget
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.schema import IJSONField
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

import copy
import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


@adapter(IJSONField, IBlocks, Interface)
@implementer(IFieldSerializer)
class BlocksJSONFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        value = copy.deepcopy(self.get_value())

        # Resolve UID links
        if self.field.getName() == "blocks":
            for block in value.values():
                if block.get("@type") == "text":
                    self.resolve_links(block)
        return json_compatible(value)

    def resolve_links(self, block):
        entity_map = block.get("text", {}).get("entityMap", {})
        for entity in entity_map.values():
            if entity.get("type") != "LINK":
                continue
            href = entity.get("data", {}).get("url", "")
            before = href  # noqa
            if href:
                match = RESOLVEUID_RE.match(href)
                if match is not None:
                    uid, suffix = match.groups()
                    href = uuidToURL(uid)
                    if href is None:
                        continue
                    if suffix:
                        href += "/" + suffix
                    else:
                        primary_field_url = self.get_primary_field_target_url(uid)
                        href = primary_field_url if primary_field_url else href
                    entity["data"]["href"] = href
                    entity["data"]["url"] = href
                    print("SERIALIZE " + before + " -> " + href)  # noqa

    def get_primary_field_target_url(self, uid):
        target_object = uuidToObject(uid)
        if not target_object:
            return
        adapter = queryMultiAdapter((target_object, self.request),
                                    IObjectPrimaryFieldTarget)
        if adapter:
            return adapter()
