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

    def __call__(self):
        sharing_view = getMultiAdapter((self.context, self.request),
                                       name='sharing')
        local_roles = sharing_view.existing_role_settings()

        # We remove the disabled flag. The entry isn't disabled, but just used
        # as a flag for the Plone template to prevent removing a users own
        # entry.
        entries = []
        for role in local_roles:
            if 'disabled' in role:
                del role['disabled']
            entries.append(role)

        available_roles = [r['id'] for r in sharing_view.roles()]
        return {'inherit': getattr(aq_base(self.context),
                                   '__ac_local_roles_block__',
                                   False),
                'entries': entries,
                'available_roles': available_roles}
