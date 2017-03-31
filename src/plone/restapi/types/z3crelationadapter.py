# -*- coding: utf-8 -*-
from plone.restapi.types.interfaces import IJsonSchemaProvider
from z3c.relationfield.interfaces import IRelationList
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface

from plone.restapi.types.adapters import ListJsonSchemaProvider


@adapter(IRelationList, Interface, Interface)
@implementer(IJsonSchemaProvider)
class ChoiceslessRelationListSchemaProvider(ListJsonSchemaProvider):

    def get_items(self):
        """Get items properties."""
        value_type_adapter = getMultiAdapter(
            (self.field.value_type, self.context, self.request),
            IJsonSchemaProvider)

        # Prevent rendering all choices.
        value_type_adapter.should_render_choices = False

        return value_type_adapter.get_schema()
