from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from z3c.relationfield.interfaces import IRelationChoice
from z3c.relationfield.interfaces import IRelationList
from z3c.relationfield.interfaces import IRelationValue
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.interface import implementer
from zope.interface import Interface


@adapter(IRelationValue)
@implementer(IJsonCompatible)
def relationvalue_converter(value):
    if value.to_object:
        summary = getMultiAdapter(
            (value.to_object, getRequest()), ISerializeToJsonSummary
        )()
        return json_compatible(summary)


@adapter(IRelationChoice, IDexterityContent, Interface)
@implementer(IFieldSerializer)
class RelationChoiceFieldSerializer(DefaultFieldSerializer):
    def __call__(self):
        result = json_compatible(self.get_value())
        # Enhance information based on the content type in relation
        if result is None:
            return None
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        portal_url = portal.absolute_url()
        rel_url = result["@id"]
        if not rel_url.startswith(portal_url):
            raise RuntimeError(
                f"Url must start with portal url. [{portal_url} <> {rel_url}]"
            )
        rel_path = rel_url[len(portal_url) + 1 :]
        rel_obj = portal.unrestrictedTraverse(rel_path, None)
        serializer = getMultiAdapter((rel_obj, self.field, self.context, self.request))
        result = serializer()
        return result


@adapter(IRelationList, IDexterityContent, Interface)
@implementer(IFieldSerializer)
class RelationListFieldSerializer(DefaultFieldSerializer):
    pass
