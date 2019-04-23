# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.expansion import expandable_elements
from Products.CMFCore.interfaces._tools import IMemberData
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import Interface
from zope.interface import implementer
from zope.publisher.interfaces import IRequest
from zope.schema import getFieldNames

try:
    # Plone 5
    from plone.app.users.browser.userdatapanel import getUserDataSchema
    HAS_TTW_SCHEMAS = True
except ImportError:
    # Plone 4.3
    from plone.app.users.userdataschema import IUserDataSchemaProvider
    HAS_TTW_SCHEMAS = False


def get_groups(portal, request, user):
    group_tool = getToolByName(portal, 'portal_groups')
    group_ids = group_tool.getGroupsForPrincipal(user)
    group_ids = list(set(group_ids) - set(['AuthenticatedUsers']))
    groups = []
    for group_id in group_ids:
        group = group_tool.getGroupById(group_id)
        if group:
            groups.append(
                getMultiAdapter((group, request),
                                interface=ISerializeToJsonSummary)())
    return groups


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

        data = {
            '@id': '{}/@users/{}'.format(portal.absolute_url(), user.id),
            'id': user.id,
            'username': user.getUserName(),
            'roles': roles,
        }

        if HAS_TTW_SCHEMAS:
            schema = getUserDataSchema()
        else:
            util = getUtility(IUserDataSchemaProvider)
            schema = util.getSchema()

        for name in getFieldNames(schema):
            if name == 'portrait':
                memberdata = getToolByName(portal, 'portal_memberdata')
                if user.id in memberdata.portraits:
                    value = '{}/portal_memberdata/portraits/{}'.format(
                        portal.absolute_url(), user.id)
                else:
                    value = None
            elif name == 'pdelete':
                continue
            else:
                value = user.getProperty(name, '')
                if value == '':
                    value = None
                if value:
                    value = safe_unicode(value)
            data[name] = value

        # Insert expandable elements
        data.update(expandable_elements(self.context, self.request))

        return data


@implementer(IExpandableElement)
@adapter(IMemberData, Interface)
class UserGroupsExpander(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'user-groups': {
                '@id': '{}/@user-groups'.format(self.context.absolute_url()),
            },
        }
        if expand:
            result['user-groups']['groups'] = get_groups(
                self.context, self.request, self.context)
        return result


@implementer(ISerializeToJson)
@adapter(IMemberData, IRequest)
class SerializeUserToJson(BaseSerializer):
    pass


@implementer(ISerializeToJsonSummary)
@adapter(IMemberData, IRequest)
class SerializeUserToJsonSummary(BaseSerializer):
    pass
