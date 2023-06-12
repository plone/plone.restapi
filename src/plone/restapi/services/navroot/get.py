# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement, ISerializeToJson
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Navroot:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"navroot": {"@id": f"{self.context.absolute_url()}/@navroot"}}
        if not expand:
            return result

        portal_state = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        )
        # We need to unset expansion here, otherwise we get infinite recursion
        self.request.form["expand"] = ""

        result["navroot"]["navroot"] = getMultiAdapter(
            (portal_state.navigation_root(), self.request),
            ISerializeToJson,
        )()

        return result


class NavrootGet(Service):
    def reply(self):
        navroot = Navroot(self.context, self.request)
        return navroot(expand=True)["navroot"]
