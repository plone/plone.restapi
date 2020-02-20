# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.restapi.behaviors import IBlocks
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from plone.schema import IJSONField
from plone.uuid.interfaces import IUUID
from plone.uuid.interfaces import IUUIDAware
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest


def path2uid(context, portal, href):
    # unrestrictedTraverse requires a string on py3. see:
    # https://github.com/zopefoundation/Zope/issues/674
    if not href:
        return ''
    portal_url = portal.absolute_url()
    portal_path = '/'.join(portal.getPhysicalPath())
    path = href
    context_url = context.absolute_url()
    relative_up = len(context_url.split("/")) - len(portal_url.split("/"))
    if path.startswith(portal_url):
        path = path[len(portal_url) + 1 :]
    if not path.startswith(portal_path):
        path = '{portal_path}/{path}'.format(
            portal_path=portal_path, path=path.lstrip("/")
        )
    obj = portal.unrestrictedTraverse(path, None)
    if obj is None:
        return href
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
    def __call__(self, value):
        value = super(BlocksJSONFieldDeserializer, self).__call__(value)

        # Convert absolute links to resolveuid
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        if self.field.getName() == "blocks":
            for block in value.values():
                if block.get("@type") == "text":
                    entity_map = block.get("text", {}).get("entityMap", {})
                    for entity in entity_map.values():
                        if entity.get("type") == "LINK":
                            href = entity.get("data", {}).get("url", "")
                            deserialized_href = path2uid(
                                context=self.context, portal=portal, href=href
                            )
                            entity["data"]["href"] = deserialized_href
                            entity["data"]["url"] = deserialized_href
                            print(
                                "DESERIALIZE "
                                + href
                                + " -> "
                                + deserialized_href
                            )
                else:
                    # standard blocks can have an "url" or "href" field
                    url = block.get("url", "")
                    href = block.get("href", "")
                    deserialized_url = path2uid(
                        context=self.context, portal=portal, href=url
                    )
                    deserialized_href = path2uid(
                        context=self.context, portal=portal, href=href
                    )
                    block["url"] = deserialized_url
                    block["href"] = deserialized_href
                    print("DESERIALIZE " + url + " -> " + deserialized_url)
                    print("DESERIALIZE " + href + " -> " + deserialized_href)
        return value
