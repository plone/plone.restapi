from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer
from plone.restapi.services.contenttypes import ContentTypesService
from plone.restapi.types.utils import _deserialize_schema_values
from plone.restapi.typesettings.interfaces import ITypeCreation
from plone.restapi.typesettings.manage import copy_type
from plone.restapi.typesettings.manage import create_type
from zExceptions import BadRequest


class ContentTypesPost(ContentTypesService):
    def reply(self):
        if self.params:
            raise BadRequest(f"Create content types at {self.url()}")
        body, errors = _deserialize_schema_values(
            self.context,
            self.request,
            ITypeCreation,
            self.json_body(),
            partial=False,
            strict=True,
        )
        if errors:
            self.raise_errors(errors)
        type_id = body.get("id") or idnormalizer.normalize(body["title"]).replace(
            "-", "_"
        )
        if type_id in self.types_tool:
            self.request.response.setStatus(409)
            return {
                "error": {
                    "type": "Conflict",
                    "message": "A content type with this ID already exists",
                }
            }
        self.check_id(type_id)
        if body.get("copy_from"):
            source = self.types_tool.get(body["copy_from"])
            if not IDexterityFTI.providedBy(source):
                self.raise_errors(
                    [
                        {
                            "field": "copy_from",
                            "message": "Expected the ID of a Dexterity content type",
                            "error": None,
                        }
                    ]
                )
            fti = copy_type(
                self.types_tool,
                source,
                type_id,
                body["title"],
                body.get("description"),
                self.request,
            )
        else:
            fti = create_type(
                self.types_tool, type_id, body["title"], body.get("description")
            )
        result = self.serialize(fti)
        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", result["@id"])
        return result

    def check_id(self, type_id):
        """Apply the ID rules of the types tool, like reserved names."""
        error = None
        if not type_id or "/" in type_id:
            error = "Invalid content type ID"
        else:
            try:
                self.types_tool._checkId(type_id)
            except BadRequest as exc:
                error = str(exc)
        if error:
            self.raise_errors([{"field": "id", "message": error, "error": None}])
