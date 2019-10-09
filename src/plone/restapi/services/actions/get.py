# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from Products.CMFCore.interfaces import IActionCategory
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Actions(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"actions": {"@id": "{}/@actions".format(self.context.absolute_url())}}
        if not expand:
            return result

        context_state = getMultiAdapter(
            (self.context, self.request), name="plone_context_state"
        )

        categories = self.request.form.get("categories", self.all_categories)
        data = {}
        for category in categories:
            category_action_data = []
            actions = context_state.actions(category=category)
            for action in actions:
                category_action_data.append(
                    {
                        "title": translate(action["title"], context=self.request),
                        "id": action["id"],
                        "icon": action["icon"],
                    }
                )
            data[category] = category_action_data
        return {"actions": data}

    @property
    def all_categories(self):
        portal_actions = getToolByName(self.context, "portal_actions")
        categories = []
        for id, obj in portal_actions.objectItems():
            if IActionCategory.providedBy(obj):
                categories.append(id)
        return categories


class ActionsGet(Service):
    def reply(self):
        actions = Actions(self.context, self.request)
        return actions(expand=True)["actions"]
