from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from plone.app.customerize import registration
from zope.component import getUtilitiesFor
from plone.dexterity.interfaces import IDexterityFTI
from plone import api
from zope.globalrequest import getRequest


class ContentGet(Service):
    """Returns a serialized content object."""

    @classmethod
    def __restapi_doc_component_schemas_extension__(cls):
        doc = super(ContentGet, cls).__restapi_doc_component_schemas_extension__()

        # recupero le interfacce per cui il service è stato registrato
        services = [
            i
            for i in registration.getViews(IBrowserRequest)
            if getattr(i.factory, "__name__", "") == cls.__name__
        ]
        required_interfaces = [x.required[0] for x in services]

        # recupero i tipi di contenuto che implementano quelle interfacce
        ftis = []
        for name, fti in getUtilitiesFor(IDexterityFTI):
            if name == "Plone Site":
                instance = api.portal.get()
            else:
                try:
                    instance = fti.constructInstance(api.portal.get(), id=name)
                except Exception:
                    instance = getattr(api.portal.get(), "name", None)

            for interface in required_interfaces:
                if interface.providedBy(instance):
                    ftis.append((fti, instance))
                    break

        # chiamo il serializer registrato per ISerializeToJson per ogni tipo
        # di contenuto
        definition = {}
        for fti in ftis:
            serializer = queryMultiAdapter((fti[1], getRequest()), ISerializeToJson)
            if method := getattr(serializer, "__restapi_doc_component_schema__", None):
                definition.update(**method(fti[1], getRequest()))

        return definition

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
                                "schema": {
                                    "$ref": "$ContextType",
                                }
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
