# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from Products.CMFCore.interfaces._tools import IMemberData
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


@implementer(ISerializeToJson)
@adapter(IMemberData, Interface)
class SerializeUserToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        user = self.context
        portal = getSite()
        return {
            '@id': '{}/@users/{}'.format(
                portal.absolute_url(),
                user.id
            ),
            'id': user.id,
            'email': user.getProperty('email'),
            'username': user.getUserName(),
            'fullname': user.getProperty('fullname'),
            'home_page': user.getProperty('home_page'),
            'description': user.getProperty('description'),
            'location': user.getProperty('location')
        }
