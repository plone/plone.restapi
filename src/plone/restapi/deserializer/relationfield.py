from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.deserializer.dxfields import DefaultFieldDeserializer
from plone.restapi.interfaces import IFieldDeserializer
from Products.CMFCore.utils import getToolByName
from z3c.relationfield.interfaces import IRelationChoice
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import implementer
from zope.intid.interfaces import IIntIds
from zope.publisher.interfaces.browser import IBrowserRequest


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
            resolved_by = "intid"
        elif isinstance(value, str):
            portal = getMultiAdapter(
                (self.context, self.request), name="plone_portal_state"
            ).portal()
            portal_url = portal.absolute_url()
            if value.startswith(portal_url):
                # Resolve by URL
                obj = portal.restrictedTraverse(value[len(portal_url) + 1 :], None)
                resolved_by = "URL"
            elif value.startswith("/"):
                # Resolve by path
                obj = portal.restrictedTraverse(value.lstrip("/"), None)
                resolved_by = "path"
            else:
                # Resolve by UID
                catalog = getToolByName(self.context, "portal_catalog")
                brain = catalog(UID=value)
                if brain:
                    obj = brain[0].getObject()
                resolved_by = "UID"

        if obj is None:
            self.request.response.setStatus(400)
            raise ValueError(f"Could not resolve object for {resolved_by}={value}")

        self.field.validate(obj)
        return obj
