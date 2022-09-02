from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.batching import HypermediaBatch
from Products.CMFCore.interfaces._tools import IMemberData
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IRequest
from zope.schema import getFieldNames
from plone.app.users.browser.userdatapanel import getUserDataSchema


class BaseSerializer:
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
        roles = sorted(list(set(roles) - {"Anonymous", "Authenticated"}))

        data = {
            "@id": f"{portal.absolute_url()}/@users/{user.id}",
            "id": user.id,
            "username": user.getUserName(),
            "roles": roles,
        }

        schema = getUserDataSchema()

        for name in getFieldNames(schema):
            if name == "portrait":
                membership = getToolByName(portal, "portal_membership")
                memberdata = getToolByName(portal, "portal_memberdata")
                safe_id = membership._getSafeMemberId(user.id)
                if safe_id in memberdata.portraits:
                    value = f"{portal.absolute_url()}/@portrait/{safe_id}"
                else:
                    value = None
            elif name == "pdelete":
                continue
            else:
                value = user.getProperty(name, "")
                if value == "":
                    value = None
                if value:
                    value = safe_unicode(value)
            data[name] = value

        return data


@implementer(ISerializeToJsonSummary)
@adapter(IMemberData, IRequest)
class SerializeUserToJsonSummary(BaseSerializer):
    def __call__(self):
        data = super().__call__()
        return data


@implementer(ISerializeToJson)
@adapter(IMemberData, IRequest)
class SerializeUserToJson(BaseSerializer):
    def __call__(self):
        data = super().__call__()
        user = self.context
        gtool = getToolByName(self.context, "portal_groups")
        groupIds = user.getGroups()
        groups = [gtool.getGroupById(grp) for grp in groupIds]
        groups = [{"id": grp.id, "title": grp.title or grp.id} for grp in groups]
        batch = HypermediaBatch(self.request, groups)
        groups_data = {
            "@id": batch.canonical_url,
            "items_total": batch.items_total,
            "items": sorted(batch, key=lambda x: x["title"]),
        }
        if batch.links:
            groups_data["batching"] = batch.links

        data["groups"] = groups_data
        return data
