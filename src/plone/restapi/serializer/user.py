from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
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
        roles = list(set(roles) - {"Anonymous", "Authenticated"})

        data = {
            "@id": f"{portal.absolute_url()}/@users/{user.id}",
            "id": user.id,
            "username": user.getUserName(),
            "roles": roles,
        }

        schema = getUserDataSchema()

        for name in getFieldNames(schema):
            if name == "portrait":
                memberdata = getToolByName(portal, "portal_memberdata")
                if user.id in memberdata.portraits:
                    value = "{}/portal_memberdata/portraits/{}".format(
                        portal.absolute_url(), user.id
                    )
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


@implementer(ISerializeToJson)
@adapter(IMemberData, IRequest)
class SerializeUserToJson(BaseSerializer):
    pass


@implementer(ISerializeToJsonSummary)
@adapter(IMemberData, IRequest)
class SerializeUserToJsonSummary(BaseSerializer):
    pass
