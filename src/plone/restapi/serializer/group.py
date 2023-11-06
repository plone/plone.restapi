from AccessControl import getSecurityManager
from plone.restapi.batching import HypermediaBatch
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from Products.CMFCore.permissions import ManagePortal
from Products.PlonePAS.interfaces.group import IGroupData
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


class BaseSerializer:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    @property
    def is_zope_manager(self):
        return getSecurityManager().checkPermission(ManagePortal, self.context)

    def can_delete(self, roles):
        if self.is_zope_manager:
            return True
        return "Manager" not in roles

    def __call__(self):
        group = self.context
        portal = getSite()
        roles = group.getRoles()

        return {
            "@id": f"{portal.absolute_url()}/@groups/{group.id}",
            "id": group.id,
            "groupname": group.getGroupName(),
            "email": group.getProperty("email"),
            "title": group.getProperty("title"),
            "description": group.getProperty("description"),
            "roles": roles,
            "can_delete": self.can_delete(roles),
        }


@implementer(ISerializeToJsonSummary)
@adapter(IGroupData, Interface)
class SerializeGroupToJsonSummary(BaseSerializer):
    pass


@implementer(ISerializeToJson)
@adapter(IGroupData, Interface)
class SerializeGroupToJson(BaseSerializer):
    def __call__(self):
        data = super().__call__()
        group = self.context
        members = group.getGroupMemberIds()
        batch = HypermediaBatch(self.request, members)
        members_data = {
            "@id": batch.canonical_url,
            "items_total": batch.items_total,
            "items": sorted(batch),
        }
        if batch.links:
            members_data["batching"] = batch.links

        data["members"] = members_data
        return data
