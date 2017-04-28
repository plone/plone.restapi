# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.component.hooks import getSite


class HistoryGet(Service):

    def reply(self):
        content_history_viewlet = ContentHistoryViewlet(
            self.context,
            self.request,
            None,
            None
        )
        site_url = getSite().absolute_url()
        content_history_viewlet.navigation_root_url = site_url
        content_history_viewlet.site_url = site_url
        history = content_history_viewlet.fullHistory()

        unwanted_keys = [
            'diff_current_url',
            'diff_previous_url',
            'preview_url',
            'actor_home',
            'actorid',
            'revert_url',
        ]

        for item in history:
            item['actor'] = {
                '@id': '{}/@users/{}'.format(site_url, item['actorid']),
                'id': item['actorid'],
                'fullname': item['actor'].get('fullname'),
                'username': item['actor'].get('username'),
            }

            if item['type'] == 'versioning':
                item['content_url'] = '{}/?version_id={}'.format(
                    self.context.absolute_url(),
                    item['version_id']
                )

                # If a revert_url is present, then CMFEditions has checked our
                # permissions.
                item['may_revert'] = bool(item.get('revert_url'))

            # clean up
            for key in unwanted_keys:
                if key in item:
                    del item[key]

        return json_compatible(history)
