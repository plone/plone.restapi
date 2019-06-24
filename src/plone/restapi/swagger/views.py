# -*- coding: UTF-8 -*-
import json

from plone import api
from Products.Five.browser import BrowserView


def get_swagger_settings(portal_url):
    return {
        "authentication_allowed": True,
        "base_url": None,
        "auth_storage_search_keys": ["auth"],
        "base_configuration": {
            "openapi": "3.0.0",
            "info": {
                "version": "1.0",
                "title": "Not Guillotina",
                "description": "The REST Resource API",
                "servers": [
                     {
                        "url": portal_url
                     }
                ],
                "paths": {},
                "security": [
                    {
                        "basicAuth": []
                    },
                    {
                        "bearerAuth": []
                    },
                ],
                "components": {
                    "securitySchemes": {
                        "basicAuth": {
                            "type": "http",
                            "scheme": "basic"
                        },
                        "bearerAuth": {
                            "type": "http",
                            "scheme": "bearer",
                            "bearerFormat": "JWT"
                        }
                    }
                },
            },
        }
    }


class SwaggerDocs(BrowserView):

    def config(self):
        portal_url = api.portal.get().absolute_url()
        return {
            'base_url': portal_url,
            'swagger_settings': json.dumps(get_swagger_settings(portal_url),
                                           indent=4),
            'initial_swagger_url': portal_url,
        }
