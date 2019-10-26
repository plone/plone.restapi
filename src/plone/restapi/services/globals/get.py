# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


REGISTRY_MAP = {
    'can_register': 'plone.enable_self_reg',
    'can_set_password': 'plone.enable_user_pwd_choice',
    'use_email_for_login': 'plone.use_email_as_login'
}

_marker = object()

@implementer(IPublishTraverse)
class GlobalsGet(Service):

    def __init__(self, context, request):
        super(GlobalsGet, self).__init__(context, request)
        self.values_to_return = [
            'can_register',
            'can_set_password',
            'use_email_for_login',
        ]
        if self.has_manager_permission():
            # Add more entries if the user is manager?
            pass

    def has_manager_permission(self):
        sm = getSecurityManager()
        return sm.checkPermission("Manage portal", self.context)

    def reply(self):
        registry = getUtility(IRegistry)
        results = dict()
        for key in self.values_to_return:
            val = registry.get(REGISTRY_MAP[key], _marker)
            if val is not _marker:
                results[key] = val
        return results
