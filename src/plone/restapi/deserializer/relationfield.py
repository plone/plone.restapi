# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from z3c.relationfield.interfaces import IRelationChoice
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest
import six


@implementer(IFieldDeserializer)
@adapter(IRelationChoice, IDexterityContent, IBrowserRequest)
class RelationChoiceFieldDeserializer(DefaultFieldDeserializer):
    def __call__(self, value):
        obj = None

        if isinstance(value, dict):
            # We are trying to deserialize the output of a serialization
            # which is enhanced, extract it and put it on the loop again
            value = value["@id"]

        if isinstance(value, int):
            # Resolve by intid
            intids = queryUtility(IIntIds)
            obj = intids.queryObject(value)
        elif isinstance(value, six.string_types):
            if six.PY2 and isinstance(value, six.text_type):
                value = value.encode("utf8")
            portal = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            ).portal()
            portal_url = portal.absolute_url()
            if value.startswith(portal_url):
                # Resolve by URL
                obj = portal.restrictedTraverse(value[len(portal_url) + 1 :], None)
            elif value.startswith("/"):
                # Resolve by path
                obj = portal.restrictedTraverse(value.lstrip("/"), None)
            else:
                # Resolve by UID
                catalog = getToolByName(self.context, "portal_catalog")
                brain = catalog(UID=value)
                if brain:
                    obj = brain[0].getObject()

        self.field.validate(obj)
        return obj
