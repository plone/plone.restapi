# -*- coding: utf-8 -*-
from plone.app.linkintegrity.utils import linkintegrity_enabled
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class LinkintegrityGet(Service):
    """
    Return a list of breaches from p.a.linkintegrity view
    """

    def reply(self):
        if not linkintegrity_enabled():
            return json_compatible([])
        links_info = self.context.restrictedTraverse("@@delete_confirmation_info")
        breaches = links_info.get_breaches()

        for breach in breaches:
            breach["target"]["@id"] = breach["target"]["url"]
            breach["target"]["@type"] = breach["target"]["portal_type"]
            del breach["target"]["url"]
            del breach["target"]["portal_type"]

            for source in breach.get("sources", []):
                source["@id"] = source["url"]
                del source["url"]

        return json_compatible(breaches)
