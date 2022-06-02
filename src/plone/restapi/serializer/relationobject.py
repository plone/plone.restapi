from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IRelationObjectSerializer
from plone.restapi.serializer.converters import json_compatible
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface
from zope.interface import alsoProvides
from plone.app.contenttypes.interfaces import IImage
from plone.namedfile.interfaces import INamedImageField
from z3c.relationfield.interfaces import IRelationChoice

import logging


log = logging.getLogger(__name__)


@adapter(IDexterityContent, IRelationChoice, IDexterityContent, Interface)
@implementer(IRelationObjectSerializer)
class DefaultRelationObjectSerializer:
    def __init__(self, rel_obj, field, context, request):
        self.context = context
        self.request = request
        self.field = field
        self.rel_obj = rel_obj

    def __call__(self):
        obj = self.rel_obj
        # Start from the values of the default field serializer
        result = json_compatible(self.get_value())
        if result is None:
            return None
        # Add some more values from the object in relation
        additional = {
            "id": obj.id,
            "created": obj.created(),
            "modified": obj.modified(),
            "UID": obj.UID(),
        }
        result.update(additional)
        return json_compatible(result)

    def get_value(self, default=None):
        return getattr(self.field.interface(self.context), self.field.__name__, default)


class FieldSim:
    def __init__(self, name, provides):
        self.__name__ = name
        alsoProvides(self, provides)

    def get(self, context):
        return getattr(context, self.__name__)


class FieldRelationObjectSerializer(DefaultRelationObjectSerializer):
    """The relationship object is treatable like a field

    So we can reuse the serialization for that specific field.
    """

    field_name = None
    field_interface = None

    def __call__(self):
        field = FieldSim(self.field_name, self.field_interface)
        result = super().__call__()
        if result is None:
            return None
        # Reuse a serializer from dxfields
        serializer = getMultiAdapter((field, self.rel_obj, self.request))
        # Extend the default values with the content specific ones
        additional = serializer()
        if additional is not None:
            result.update(additional)
        return result


@adapter(IImage, IRelationChoice, IDexterityContent, Interface)
class ImageRelationObjectSerializer(FieldRelationObjectSerializer):
    # The name of the attribute that contains the data object within the relation object
    field_name = "image"
    # The field adapter that we will emulate to get the serialized data for this content type
    field_interface = INamedImageField
