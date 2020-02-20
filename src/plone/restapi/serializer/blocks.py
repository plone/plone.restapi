# -*- coding: utf-8 -*-
from plone.outputfilters.browser.resolveuid import uuidToURL
from plone.restapi.behaviors import IBlocks
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.schema import IJSONField
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import copy
import re


RESOLVEUID_RE = re.compile("^[./]*resolve[Uu]id/([^/]*)/?(.*)$")


@adapter(IJSONField, IBlocks, Interface)
@implementer(IFieldSerializer)
class BlocksJSONFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        if self.field.getName() != "blocks":
            return json_compatible(self.get_value())
        value = copy.deepcopy(self.get_value())
        for block in value.values():
            if block.get("@type") == "text":
                entity_map = block.get("text", {}).get("entityMap", {})
                for entity in entity_map.values():
                    if entity.get("type") == "LINK":
                        href = entity.get("data", {}).get("url", "")
                        resolved_href = self.uid_to_url(href=href)
                        if resolved_href:
                            entity["data"]["href"] = resolved_href
                            entity["data"]["url"] = resolved_href
            else:
                # standard blocks can have an "url" or "href" field
                url = block.get('url', '')
                href = block.get('href', '')
                resolved_href = self.uid_to_url(href=href)
                resolved_url = self.uid_to_url(href=url)
                if resolved_href:
                    block["href"] = resolved_href
                if resolved_url:
                    block["url"] = resolved_url
        return json_compatible(value)

    def uid_to_url(self, href):
        if not href:
            return ''
        match = RESOLVEUID_RE.match(href)
        if match is not None:
            uid, suffix = match.groups()
            href = uuidToURL(uid)
            if href is None:
                return ''
            if suffix:
                href += "/" + suffix
        return href
