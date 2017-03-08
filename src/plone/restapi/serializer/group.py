# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from Products.PlonePAS.interfaces.group import IGroupData
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IGroupData, Interface)
class SerializeGroupToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        group = self.context
        portal = getSite()
        return {
            '@id': '{}/@groups/{}'.format(
                portal.absolute_url(),
                group.id
            ),
            'id': group.id,
            'groupname': group.getGroupName(),
            'email': group.getProperty('email'),
            'title': group.getProperty('title'),
            'description': group.getProperty('description')
        }
