# -*- coding: utf-8 -*-
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.utils import getToolByName
from plone import api
from plone.restapi.services import Service
from zope.i18n import translate


class ActionsGet(Service):

    @property
    def all_categories(self):
        portal_actions = getToolByName(self.context, 'portal_actions')
        categories = []
        for id, obj in portal_actions.objectItems():
            if IActionCategory.providedBy(obj):
                categories.append(id)
        return categories

    def reply(self):
        context_state = api.content.get_view(name='plone_context_state',
                                             context=self.context,
                                             request=self.request)
        categories = self.request.form.get('categories',
                                           self.all_categories)
        data = {}
        for category in categories:
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
