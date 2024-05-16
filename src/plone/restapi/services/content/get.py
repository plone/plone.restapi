from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter


class ContentGet(Service):
    """Returns a serialized content object."""

    @classmethod
    def __restapi_doc__(cls):
        return {
            "get": {
                "summary": "Content",
                "description": "Content data",
                "responses": {
                    "200": {
                        "description": "Success",
                        "content": {
                            "application/json": {
                                "schema": {"type": "object", "$ref": "$ContextType"}
                            }
                        },
                    },
                    "501": {
                        "description": "ServerError",
                        "content": {
                            "application/json": {
                                "schema": {"$ref": "#/components/schemas/ErrorResponse"}
                            }
                        },
                    },
                },
            }
        }

    def reply(self):
        serializer = queryMultiAdapter((self.context, self.request), ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message="No serializer available."))

        return serializer(version=self.request.get("version"))
