# -*- coding: utf-8 -*-
from plone.app.linkintegrity.utils import linkintegrity_enabled
from plone.app.uuid.utils import uuidToObject
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
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

        catalog = getToolByName(self.context, "portal_catalog")
        result = []
        for uid in uids:
            item = uuidToObject(uid)
            item_path = "/".join(item.getPhysicalPath())
            links_info = item.restrictedTraverse("@@delete_confirmation_info")
            breaches = links_info.get_breaches()
            data = getMultiAdapter((item, self.request), ISerializeToJsonSummary)()
            data["breaches"] = []
            for breach in breaches:
                if breach["target"]["uid"] not in uids:
                    uids.append(breach["target"]["uid"])
                    continue
                for source in breach.get("sources", []):
                    # remove unwanted data
                    source["@id"] = source["url"]
                    del source["url"]
                    del source["accessible"]
                    data["breaches"].append(source)
            # subtract one because we don't want to count item_path itself
            data["items_total"] = len(catalog(path=item_path)) - 1
            result.append(data)
        return json_compatible(result)
