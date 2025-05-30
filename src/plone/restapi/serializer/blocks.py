from plone import api
from plone.restapi.bbb import IPloneSiteRoot
from plone.restapi.behaviors import IBlocks
from plone.restapi.blocks import iter_block_transform_handlers
from plone.restapi.blocks import visit_blocks
from plone.restapi.deserializer.blocks import iterate_children
from plone.restapi.deserializer.blocks import SlateBlockTransformer
from plone.restapi.deserializer.blocks import transform_links
from plone.restapi.interfaces import IBlockFieldSerializationTransformer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.serializer.utils import resolve_uid
from plone.restapi.serializer.utils import uid_to_url
from plone.schema import IJSONField
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserRequest

import copy
import os
import re


@adapter(IJSONField, Interface, Interface)
@implementer(IFieldSerializer)
class BlocksJSONFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        value = copy.deepcopy(self.get_value())

        if self.field.getName() == "blocks":
            for block in visit_blocks(self.context, value):
                new_block = block.copy()
                for handler in iter_block_transform_handlers(
                    self.context, block, IBlockFieldSerializationTransformer
                ):
                    new_block = handler(new_block)
                block.clear()
                block.update(new_block)
        else:
            fake_block = {"@type": "jsonfield", "value": value}
            for handler in iter_block_transform_handlers(
                self.context, fake_block, IBlockFieldSerializationTransformer
            ):
                fake_block = handler(fake_block)
            value = fake_block["value"]

        return json_compatible(value)


class ResolveUIDSerializerBase:
    order = 1
    block_type = None
    fields = ["url", "href", "preview_image"]
    disabled = os.environ.get("disable_transform_resolveuid", False)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        return self._process_data(block)

    def _process_data(self, data, field=None):
        if isinstance(data, str) and field in self.fields:
            return uid_to_url(data)
        if isinstance(data, list):
            return [self._process_data(data=value, field=field) for value in data]
        if isinstance(data, dict):
            fields = ["value"] if data.get("@type") == "URL" else []
            fields.append("@id")
            fields.extend(self.fields)
            newdata = {}
            for field in fields:
                if field not in data or not isinstance(data[field], str):
                    continue
                newdata[field], brain = resolve_uid(data[field])
                if brain is not None and "image_scales" not in newdata:
                    newdata["image_scales"] = json_compatible(
                        getattr(brain, "image_scales", None)
                    )
            result = {
                field: (
                    newdata[field]
                    if field in newdata
                    else self._process_data(data=newdata.get(field, value), field=field)
                )
                for field, value in data.items()
            }
            if newdata.get("image_scales"):
                result["image_scales"] = newdata["image_scales"]
            return result
        return data


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
@adapter(Interface, IBrowserRequest)
class ResolveUIDSerializer(ResolveUIDSerializerBase):
    """UID-to-URL transformer for all content types"""


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


class SlateTableBlockSerializerBase(SlateBlockSerializerBase):
    """SlateBlockSerializerBase."""

    order = 100
    block_type = "slateTable"

    def __call__(self, block):
        """call"""
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


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class SlateTableBlockSerializer(SlateTableBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class SlateTableBlockSerializerRoot(SlateTableBlockSerializerBase):
    """Serializer for site root"""


class TeaserBlockSerializerBase:
    order = 0
    block_type = "teaser"

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block):
        return self._process_data(block)

    def _process_data(self, data, field=None):
        value = data.get("href", "")
        if value:
            if "overwrite" not in data:
                # A block without this option is old and keeps the behavior
                # where data is not dynamically pulled from the href
                data["overwrite"] = True
                return data

            if isinstance(value, str):
                url = value
                value = [{"@id": url}]
            else:
                url = value[0].get("@id", "")
            brain = url_to_brain(url)
            if brain is not None:
                serialized_brain = getMultiAdapter(
                    (brain, self.request), ISerializeToJsonSummary
                )()

                if not data.get("overwrite"):
                    # Update fields at the top level of the block data
                    for key in ["title", "description", "head_title"]:
                        if key in serialized_brain:
                            data[key] = serialized_brain[key]

                # We return the serialized brain.
                value[0].update(serialized_brain)
                data["href"] = value
            elif not url.startswith("http"):
                # Source not found; clear out derived fields
                data["href"] = []
        return data


@implementer(IBlockFieldSerializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class TeaserBlockSerializer(TeaserBlockSerializerBase):
    """Serializer for content-types with IBlocks behavior"""


RESOLVE_UID_REGEXP = re.compile("resolveuid/([^/]+)")


@implementer(IBlockFieldSerializationTransformer)
@adapter(IPloneSiteRoot, IBrowserRequest)
class TeaserBlockSerializerRoot(TeaserBlockSerializerBase):
    """Serializer for site root"""


def url_to_brain(url):
    """Find the catalog brain for a URL.

    Returns None if no item was found that is visible to the current user.
    """
    if not url:
        return
    if match := RESOLVE_UID_REGEXP.search(url):
        uid = match.group(1)
        query = {"UID": uid}
    else:
        # fallback in case the url wasn't converted to a UID
        path = "/".join(api.portal.get().getPhysicalPath()) + url
        query = {"path": {"query": path, "depth": 0}}
    catalog = api.portal.get_tool("portal_catalog")
    results = catalog.searchResults(**query)
    if results:
        return results[0]
