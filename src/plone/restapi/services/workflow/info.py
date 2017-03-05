# -*- coding: utf-8 -*-
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
import plone.api.portal


class WorkflowInfo(Service):
    """Get workflow information
    """
    def reply(self):
        wftool = plone.api.portal.get_tool('portal_workflow')
        history = wftool.getInfoFor(self.context, "review_history")

        actions = wftool.listActionInfos(object=self.context)
        transitions = []
        for action in actions:
            if action['category'] != 'workflow':
                continue

            transitions.append({
                '@id': '{}/@workflow/{}'.format(
                    self.context.absolute_url(), action['id']),
                'title': action['title'],
            })

        return {
            'history': json_compatible(history),
            'transitions': transitions,
        }
