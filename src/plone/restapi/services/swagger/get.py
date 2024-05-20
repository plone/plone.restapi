# -*- coding: utf-8 -*-
from plone import api
from plone.app.customerize import registration
from plone.restapi.services import Service
from plone.restapi.interfaces import ISerializeToJson
from Products.CMFCore.utils import getToolByName
from zope.component import getMultiAdapter
from zope.globalrequest import getRequest
from zope.publisher.interfaces.browser import IBrowserRequest

import importlib
import logging
import transaction

logger = logging.getLogger("Plone")


class SwaggerDefinitions(Service):

    def inject_schemas(self, doc, schemas):
        def inject(d):
            for k, v in d.items():
                if isinstance(v, dict):
                    inject(v)
                else:
                    if k == "$ref" and "$" in v:
                        d[k] = schemas[v]

        inject(doc)

    def get_services_by_ct(self):
        portal_types = getToolByName(api.portal.get(), "portal_types")
        services_by_ct = {}
        services = [
            i
            for i in registration.getViews(IBrowserRequest)
            if "plone.rest.zcml" in getattr(i.factory, "__module__", "")
        ]

        for portal_type in portal_types.listTypeInfo():
            portal_type_services = []

            if not getattr(portal_type, "klass", None):
                continue

            module_name = ".".join(getattr(portal_type, "klass", ".").split(".")[:-1])
            module = importlib.import_module(module_name)
            klass = getattr(
                module, getattr(portal_type, "klass", ".").split(".")[-1], None
            )

            for service in services:
                if service.required[0].implementedBy(klass):
                    portal_type_services.append(service)

            if portal_type_services:
                services_by_ct[portal_type.id.replace(" ", "")] = portal_type_services

        return services_by_ct

    def get_doc_by_service(self, service):
        # Supposed to be extended later
        doc = getattr(service.factory, "__restapi_doc__", None)
        if callable(doc):
            return doc()

    def get_doc_schemas_by_service(self, service):
        doc = getattr(
            service.factory, "__restapi_doc_component_schemas_extension__", None
        )
        if callable(doc):
            return doc()

    def reply(self):
        """
        Service to define an OpenApi definition for api
        """

        openapi_doc_boilerplate = {
            "openapi": "3.0.0",
            "info": {
                "version": "1.0.0",
                "title": api.portal.get().Title(),
                "description": f"RESTApi description for a {api.portal.get().Title()} site", # noqa
            },
            "servers": [
                {
                    "url": "http://localhost:8080/",
                    "description": "Site API",
                    "x-sandbox": False,
                    "x-healthCheck": {
                        "interval": "300",
                        "url": "https://demo.plone.org",
                        "timeout": "15",
                    },
                }
            ],
            "components": {
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                    }
                },
                "schemas": {
                    "ContentType": {
                        "type": "object",
                        "properties": {
                            "error": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "Title",
                                    },
                                },
                            }
                        },
                    }
                },
            },
            "paths": {},
            "security": [{"bearerAuth": []}],
        }

        with api.env.adopt_roles(["Manager"]):
            for ct, services in self.get_services_by_ct().items():
                doc_template = {}
                doc_template["parameters"] = []

                path_parameter = {
                    "in": "path",
                    "name": ct,
                    "required": True,
                    "description": f"Path to the {ct}",
                    "schema": {
                        "type": "string",
                        "example": "",
                    },
                }

                doc_template["parameters"].append(path_parameter)

                for service in services:
                    service_doc = self.get_doc_by_service(service)

                    if not service_doc:
                        logger.warning(
                            f"No documentation found for /{ct}/{'@' + service.name.split('@')[-1]}" # noqa
                        )
                        continue

                    doc = {**doc_template, **service_doc}

                    api_name = (
                            len(service.name.split("@")) > 1
                            and "@" + service.name.split("@")[1]
                            or ""
                    )

                    openapi_doc_boilerplate["paths"][f"/{'{' + ct + '}'}/{api_name}"] = doc

                    # Extend the components
                    component = self.get_doc_schemas_by_service(service)

                    if component:
                        openapi_doc_boilerplate["components"]["schemas"].update(component)

                    self.inject_schemas(
                        doc,
                        schemas={"$ContextType": f"#/components/schemas/{ct}"},
                    )

                transaction.abort()

            return openapi_doc_boilerplate
