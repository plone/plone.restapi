# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.interfaces import IPloneSiteRoot
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Layout(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "layout": {"@id": "{}/@layout".format(self.context.absolute_url())}
        }
        if not expand:
            return result

        if IPloneSiteRoot.providedBy(self.context):
            return result

        ttool = getToolByName(self.context, "portal_types")
        ptype = getattr(self.context, 'portal_type')
        if not ptype:
            return result

        fti = ttool[ptype]
        schema = fti.lookupSchema()
        for field in schema:
            if field.endswith('blocks') or field.endswith('blocks_layout'):
                result["layout"][field] = json_compatible(schema[field].default)
        return result


class LayoutGet(Service):
    """Get layout information"""

    def reply(self):
        info = Layout(self.context, self.request)
        return info(expand=True)["layout"]
