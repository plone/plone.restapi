# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.rest import Service
from plone.restapi.serializer.converters import json_compatible


class WorkflowInfo(Service):
    """Get workflow information
    """
    def render(self):
        wftool = getToolByName(self.context, 'portal_workflow')
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
