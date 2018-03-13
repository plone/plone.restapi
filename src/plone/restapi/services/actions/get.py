# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.i18n import translate


class ActionsGet(Service):

    def reply(self):
        context_state = api.content.get_view(name='plone_context_state',
                                             context=self.context,
                                             request=self.request)
        data = {}
        for category in ['object', 'object_buttons', 'user']:
            category_action_data = []
            actions = context_state.actions(category=category)
            for action in actions:
                category_action_data.append({
                    'title': translate(action['title'], context=self.request),
                    'id': action['id'],
                    'icon': action['icon'],
                    })
            data[category] = category_action_data
        return data
