# -*- coding: utf-8 -*-
from AccessControl.interfaces import IRoleManager
from Acquisition import aq_base
from operator import itemgetter
from plone.app.workflow.interfaces import ISharingPageRole
from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.i18n import translate
from zope.interface import implementer
from zope.interface import Interface


@adapter(IRoleManager, Interface)
@implementer(ISerializeToJson)
class SerializeLocalRolesToJson(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_title(self, role_id):
        util = queryUtility(ISharingPageRole, name=role_id)
        if not util:
            return role_id
        return util.title

    def __call__(self, search=None):
        self.request.form["search_term"] = search
        sharing_view = getMultiAdapter((self.context, self.request), name="sharing")
        local_roles = sharing_view.role_settings()

        available_roles = []
        for role in sorted(sharing_view.roles(), key=itemgetter("id")):
            util = queryUtility(ISharingPageRole, name=role["id"])
            title = util.title
            available_roles.append(
                {"id": role["id"], "title": translate(title, context=self.request)}
            )

        blocked_roles = getattr(
            aq_base(self.context), "__ac_local_roles_block__", False
        )

        return {
            "inherit": not blocked_roles,
            "entries": local_roles,
            "available_roles": available_roles,
        }
