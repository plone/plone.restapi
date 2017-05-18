# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.CMFCore.interfaces._tools import IMemberData
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IRequest


class BaseSerializer(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        user = self.context
        portal = getSite()

        # Global roles
        roles = user.getRoles()
        # Anonymous and Authenticated are pseudo roles assign automatically
        # to logged-in or logged-out users. They should not be exposed here
        roles = list(set(roles) - set(['Anonymous', 'Authenticated', ]))

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
            'location': user.getProperty('location'),
            'roles': roles,
        }


@implementer(ISerializeToJson)
@adapter(IMemberData, IRequest)
class SerializeUserToJson(BaseSerializer):
    pass


@implementer(ISerializeToJsonSummary)
@adapter(IMemberData, IRequest)
class SerializeUserToJsonSummary(BaseSerializer):
    pass
