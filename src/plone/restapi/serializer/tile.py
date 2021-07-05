from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.types import utils
from plone.tiles.interfaces import ITileType
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.interface import Interface


SERVICE_ID = "@tiles"


@implementer(ISerializeToJsonSummary)
@adapter(ITileType, Interface)
class TileSummarySerializeToJson:
    def __init__(self, tile, request):
        self.tile = tile

    def __call__(self):
        portal = getSite()
        return {
            "@id": "{}/{}/{}".format(
                portal.absolute_url(), SERVICE_ID, self.tile.__name__
            ),
            "title": self.tile.title,
            "description": self.tile.description,
            "icon": self.tile.icon,
        }


def get_jsonschema_for_tile(tile, context, request):
    """Build a complete JSON schema for the given tile."""
    schema = tile.schema

    fieldsets = utils.get_fieldsets(context, request, schema)

    # Build JSON schema properties
    properties = utils.get_jsonschema_properties(context, request, fieldsets)

    # Determine required fields
    required = []
    for field in utils.iter_fields(fieldsets):
        if field.field.required:
            required.append(field.field.getName())

    # Include field modes
    for field in utils.iter_fields(fieldsets):
        if field.mode:
            properties[field.field.getName()]["mode"] = field.mode

    return {
        "type": "object",
        "title": tile.title,
        "properties": properties,
        "required": required,
        "fieldsets": utils.get_fieldset_infos(fieldsets),
    }


@implementer(ISerializeToJson)
@adapter(ITileType, Interface)
class TileSerializeToJson:
    def __init__(self, tile, request):
        self.tile = tile
        self.request = request
        self.schema = self.tile.schema

    def __call__(self):
        portal = getSite()

        return get_jsonschema_for_tile(self.tile, portal, self.request)
