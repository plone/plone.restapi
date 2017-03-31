# -*- coding: utf-8 -*-
from AccessControl.interfaces import IRoleManager
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from Products.CMFCore.interfaces import ICatalogAware
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.event import notify
from zope.interface import implementer
from zope.interface import Interface

try:
    from plone.app.workflow.events import LocalrolesModifiedEvent
    LOCALROLES_MODIFIED_EVENT_AVAILABLE = True
except ImportError:
    # Plone < 4.3.4
    LOCALROLES_MODIFIED_EVENT_AVAILABLE = False


marker = object()


@implementer(IDeserializeFromJson)
@adapter(IRoleManager, Interface)
class DeserializeFromJson(object):
    """JSON deserializer for local roles
    """

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        data = json_body(self.request)
        sharing_view = getMultiAdapter((self.context, self.request),
                                       name='sharing')

        # inherit roles
        inherit_reindex = False
        # block can be None, so we might get False or None, so we test
        # for a marker.
        inherit = data.get('inherit', marker)
        if inherit is not marker:
            inherit_reindex = sharing_view.update_inherit(status=inherit,
                                                          reindex=False)
        # roles
        roles_reindex = False
        new_roles = data.get('entries', None)
        if new_roles is not None:
            # the roles are converted into a FrozenSet so we have to filter
            # the data structure we get.
            for user in new_roles:
                roles_list = [key for key in user['roles'] if
                              user['roles'][key]]
                user['roles'] = roles_list
            roles_reindex = sharing_view.update_role_settings(new_roles,
                                                              reindex=False)

        if ICatalogAware(self.context) and (inherit_reindex or roles_reindex):
            self.context.reindexObjectSecurity()
            if LOCALROLES_MODIFIED_EVENT_AVAILABLE:
                notify(LocalrolesModifiedEvent(self.context, self.request))
