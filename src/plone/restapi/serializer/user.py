# -*- coding: utf-8 -*-
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.CMFCore.interfaces._tools import IMemberData
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IRequest


class BaseSerializer(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, include_groups=False):
        user = self.context
        portal = getSite()

        # Global roles
        roles = user.getRoles()
        # Anonymous and Authenticated are pseudo roles assign automatically
        # to logged-in or logged-out users. They should not be exposed here
        roles = list(set(roles) - set(['Anonymous', 'Authenticated', ]))

        result = {
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
        if include_groups:
            group_tool = getToolByName(portal, 'portal_groups')
            group_ids = group_tool.getGroupsForPrincipal(user)
            group_ids = list(set(group_ids) - set(['AuthenticatedUsers']))
            groups = []
            for group_id in group_ids:
                group = group_tool.getGroupById(group_id)
                if group:
                    groups.append(
                        getMultiAdapter((group, self.request),
                                        interface=ISerializeToJsonSummary)())
            result['groups'] = groups
        return result


@implementer(ISerializeToJson)
@adapter(IMemberData, IRequest)
class SerializeUserToJson(BaseSerializer):
    pass


@implementer(ISerializeToJsonSummary)
@adapter(IMemberData, IRequest)
class SerializeUserToJsonSummary(BaseSerializer):
    pass
