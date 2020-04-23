# -*- coding: utf-8 -*-

from Acquisition import aq_parent
from plone import api
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IBlockConverter
from plone.restapi.interfaces import IFieldDeserializer
from plone.schema import IJSONField
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
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
                block_type = block_value.get("@type", '')

                convert = queryMultiAdapter((self.context, self.request),
                                            IBlockConverter,
                                            name=block_type)

                if convert is not None:
                    block_value = convert(block_value)

                value[id] = block_value

        return value


@implementer(IBlockConverter)
@adapter(IBlocks, IBrowserRequest)
class TextBlockConverter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):

        # assumes in-place mutations
        entity_map = value.get("text", {}).get("entityMap", {})

        # Convert absolute links to resolveuid
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()
        context_url = self.context.absolute_url()
        relative_up = len(context_url.split("/")) - len(portal_url.split("/"))

        for entity in entity_map.values():
            if entity.get("type") == "LINK":
                href = entity.get("data", {}).get("url", "")
                before = href  # noqa

                if href and href.startswith(portal_url):
                    path = href[len(portal_url) + 1:].encode("utf8")
                    uid, suffix = path2uid(portal, path)

                    if uid:
                        href = relative_up * "../" + "resolveuid/" + uid

                        if suffix:
                            href += suffix
                        entity["data"]["href"] = href
                        entity["data"]["url"] = href
                    print("DESERIALIZE " + before + " -> " + href)  # noqa

        return value


@implementer(IBlockConverter)
@adapter(IBlocks, IBrowserRequest)
class HTMLBlockConverter(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):

        portal_transforms = api.portal.get_tool(name='portal_transforms')
        raw_html = value.get('html', '')
        data = portal_transforms.convertTo('text/x-html-safe', raw_html,
                                           mimetype="text/html")
        html = data.getData()
        value['html'] = html

        return value
