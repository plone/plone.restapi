# -*- coding: utf-8 -*-
from plone.app.linkintegrity.utils import linkintegrity_enabled
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from plone.app.uuid.utils import uuidToObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from zope.component import getMultiAdapter


@implementer(IPublishTraverse)
class LinkintegrityPOST(Service):
    """
    Return a list of breaches from p.a.linkintegrity view
    """

    def reply(self):
        query = json_body(self.request)
        uids = query.get("uids", [])

        if not uids:
            raise BadRequest('Missing parameter "uids"')

        if not linkintegrity_enabled():
            return json_compatible([])

        result = []
        for uid in uids:
            item = uuidToObject(uid)
            links_info = item.restrictedTraverse("@@delete_confirmation_info")
            breaches = links_info.get_breaches()
            if not breaches:
                continue
            data = getMultiAdapter((item, self.request), ISerializeToJsonSummary)()
            data["breaches"] = []
            for breach in breaches:
                for source in breach.get("sources", []):
                    source["@id"] = source["url"]
                    del source["url"]
                    data["breaches"].append(source)
            result.append(data)
        return json_compatible(result)
