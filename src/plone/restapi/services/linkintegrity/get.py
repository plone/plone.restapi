# -*- coding: utf-8 -*-
from plone.app.linkintegrity.utils import linkintegrity_enabled
from plone.app.uuid.utils import uuidToObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class LinkIntegrityGet(Service):
    """
    Return a list of breaches from p.a.linkintegrity view
    """

    def reply(self):
        if not linkintegrity_enabled():
            return json_compatible([])
        query = self.request.form
        uids = query.get("uids", [])

        if not uids:
            raise BadRequest('Missing parameter "uids"')
        if not isinstance(uids, list):
            uids = [uids]

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
                    # remove unwanted data
                    source["@id"] = source["url"]
                    del source["url"]
                    del source["accessible"]
                    data["breaches"].append(source)
            result.append(data)
        return json_compatible(result)
