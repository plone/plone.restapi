# -*- coding: utf-8 -*-
import logging
import importlib
import yaml
from plone.app.customerize import registration
from Products.CMFCore.utils import getToolByName
from zope.publisher.interfaces.browser import IBrowserRequest
from plone import api
from zope.schema import getFields
from collections import OrderedDict
from copy import copy
from plone.autoform.form import AutoExtensibleForm
from plone.autoform.interfaces import IParameterizedWidget
from plone.autoform.interfaces import WIDGETS_KEY
from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.interfaces import IDexterityFTI
from plone.dexterity.utils import getAdditionalSchemata
from plone.i18n.normalizer import idnormalizer
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.serializer.converters import IJsonCompatible
from plone.restapi.types.interfaces import IJsonSchemaProvider
from plone.supermodel import serializeModel
from plone.supermodel.interfaces import FIELDSETS_KEY
from plone.supermodel.utils import mergedTaggedValueDict
from plone.supermodel.utils import syncSchema
from Products.CMFCore.utils import getToolByName
from z3c.form import form as z3c_form
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.component import queryUtility
from zope.component.hooks import getSite
from zope.globalrequest import getRequest
from zope.i18n import translate
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from plone.restapi.types.utils import get_fieldsets, get_jsonschema_properties

logger = logging.getLogger(__name__)


class Application(object):
    """ """

    @classmethod
    def run(cls):
        openapi_doc_boilerplate = {
            "openapi": "3.0.0",
            "info": {
                "version": "1.0.0",
                "title": api.portal.get().Title(),
                "description": f"RESTApi description for a {api.portal.get().Title()} site",
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
        }

        for ct, services in cls.get_services_by_ct().items():
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
                service_doc = cls.get_doc_by_service(service)

                if not service_doc:
                    logger.warning(
                        f"No documentation found for /{ct}/{'@' + service.name.split('@')[-1]}"
                    )
                    continue

                doc = {**doc_template, **service_doc}

                cls.inject_schemas(
                    doc, schemas={"$ContextType": cls.get_schema_by_ct(ct)}
                )

                api_name = (
                    len(service.name.split("@")) > 1
                    and "@" + service.name.split("@")[1]
                    or ""
                )

                openapi_doc_boilerplate["paths"][f"/{'{' + ct + '}'}/{api_name}"] = doc

                # Extend the components
                component = cls.get_doc_schemas_by_service(service)

                if component:
                    openapi_doc_boilerplate["components"]["schemas"].update(component)

        with open("openapi_doc.yaml", "w") as docfile:
            docfile.write(cls.generate_yaml_by_doc(openapi_doc_boilerplate))

    @classmethod
    def get_schema_by_ct(cls, ct):
        return "#/components/schemas/ContentType"

    @classmethod
    def inject_schemas(cls, doc, schemas):
        def inject(d):
            for k, v in d.items():
                if isinstance(v, dict):
                    inject(v)
                else:
                    if k == "$ref" and "$" in v:
                        d[k] = schemas[v]

        inject(doc)

    @classmethod
    def generate_yaml_by_doc(cls, doc):
        return yaml.safe_dump(doc)

    @classmethod
    def get_services_by_ct(cls):
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
                logger.warning(
                    f"No documentation found for {getattr(portal_type, 'id', '[Can not pick up the name]')}"
                )
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
                services_by_ct[klass.__name__] = portal_type_services

        return services_by_ct

    @classmethod
    def get_doc_by_service(cls, service):
        # Supposed to be extended later
        doc = getattr(service.factory, "__restapi_doc__", None)

        return doc

    @classmethod
    def get_doc_schemas_by_service(cls, service):
        return getattr(
            service.factory, "__restapi_doc_component_schemas_extension__", None
        )

    # @classmethod
    # def get_ct_schemas(cls):

    #     portal_types = getToolByName(api.portal.get(), "portal_types")

    #     for fti in portal_types.listTypeInfo():
    #         try:
    #             schema = fti.lookupSchema()
    #         except AttributeError:
    #             schema = None
    #             fieldsets = ()
    #             additional_schemata = ()
    #         else:
    #             additional_schemata = tuple(getAdditionalSchemata(portal_type=fti.id))
    #             fieldsets = get_fieldsets(
    #                 api.portal.get(), getRequest(), schema, additional_schemata
    #             )
    #         import pdb

    #         pdb.set_trace()


if __name__ == "__main__":
    Application.run()
