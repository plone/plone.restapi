# -*- coding: utf-8 -*-
from datetime import datetime as dt
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFPlone.utils import safe_unicode
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import six


@implementer(IPublishTraverse)
class HistoryGet(Service):
    def __init__(self, context, request):
        super(HistoryGet, self).__init__(context, request)
        self.version = None

    def publishTraverse(self, request, name):
        self.version = name
        return self

    def reply(self):
        # Traverse to historical version
        if self.version:
            serializer = queryMultiAdapter(
                (self.context, self.request), ISerializeToJson
            )
            data = serializer(version=self.version)
            return data

        # Listing historical data
        content_history_viewlet = ContentHistoryViewlet(
            self.context, self.request, None, None
        )
        site_url = getSite().absolute_url()
        content_history_viewlet.navigation_root_url = site_url
        content_history_viewlet.site_url = site_url
        history = content_history_viewlet.fullHistory()

        unwanted_keys = [
            "diff_current_url",
            "diff_previous_url",
            "preview_url",
            "actor_home",
            "actorid",
            "revert_url",
            "version_id",
        ]

        for item in history:
            item["actor"] = {
                "@id": "{}/@users/{}".format(site_url, item["actorid"]),
                "id": item["actorid"],
                "fullname": item["actor"].get("fullname"),
                "username": item["actor"].get("username"),
            }

            if item["type"] == "versioning":
                item["version"] = item["version_id"]
                item["@id"] = "{}/@history/{}".format(
                    self.context.absolute_url(), item["version"]
                )

                # If a revert_url is present, then CMFEditions has checked our
                # permissions.
                item["may_revert"] = bool(item.get("revert_url"))

            # Versioning entries use a timestamp,
            # workflow ISO formatted string
            if not isinstance(item["time"], six.string_types):
                item["time"] = dt.fromtimestamp(item["time"]).isoformat()

            # The create event has an empty 'action', but we like it to say
            # 'Create', alike the transition_title
            if item["action"] is None:
                item["action"] = "Create"

            # We want action, state and transition names translated
            if "state_title" in item:
                item["state_title"] = self.context.translate(
                    safe_unicode(item["state_title"]), context=self.request
                )

            if "transition_title" in item:
                item["transition_title"] = self.context.translate(
                    safe_unicode(item["transition_title"]), context=self.request
                )

            if "action" in item:
                item["action"] = self.context.translate(
                    safe_unicode(item["action"]), context=self.request
                )

            # clean up
            for key in unwanted_keys:
                if key in item:
                    del item[key]

        return json_compatible(history)
