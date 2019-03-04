# -*- coding: utf-8 -*-
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.PlonePAS.interfaces.group import IGroupData
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


class BaseSerializer(object):
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
            'description': group.getProperty('description'),
        }


@implementer(ISerializeToJsonSummary)
@adapter(IGroupData, Interface)
class SerializeGroupToJsonSummary(BaseSerializer):
    pass


@implementer(ISerializeToJson)
@adapter(IGroupData, Interface)
class SerializeGroupToJson(BaseSerializer):

    def __call__(self):
        data = super(SerializeGroupToJson, self).__call__()
        group = self.context
        members = group.getGroupMemberIds()
        batch = HypermediaBatch(self.request, members)

        users_data = {
            '@id': batch.canonical_url,
            'items_total': batch.items_total,
            'items': list(batch),
        }
        if batch.links:
            users_data['batching'] = batch.links

        data['users'] = users_data
        return data
