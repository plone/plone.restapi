# -*- coding: utf-8 -*-
from AccessControl.interfaces import IRoleManager
from Acquisition import aq_base

from plone.restapi.interfaces import ISerializeToJson
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@adapter(IRoleManager, Interface)
@implementer(ISerializeToJson)
class SerializeLocalRolesToJson(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, search=None):
        self.request.form['search_term'] = search
        sharing_view = getMultiAdapter((self.context, self.request),
                                       name='sharing')
        local_roles = sharing_view.role_settings()
        available_roles = [r['id'] for r in sharing_view.roles()]

        blocked_roles = getattr(
            aq_base(self.context),
            '__ac_local_roles_block__',
            False,
        )

        return {'inherit': not blocked_roles,
                'entries': local_roles,
                'available_roles': available_roles}
