# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zope.i18n import translate


class RolesGet(Service):
    __restapi_doc_definitions__ = {
        "Role": {
            "type": "object",
            "required": [
                "id",
                ],
            "properties": {
                "@id": {
                    "type": "string",
                    "example": "http://localhost:55001/plone/@roles/Manager",
                },
                "@type": {
                    "type": "string",
                    "example": "role",
                },
                "id": {
                    "type": "string",
                    "example": "Manager",
                },
                "title": {
                    "type": "string",
                    "example": "Manager",
                },
            }
        },
    }
    __restapi_doc__ = {
        "/@roles": {
            "get": {
                "summary": "Get a list of roles in the site",
                "description": ("This endpoint is only available for Users "
                                "with management permissions."),
                "consumes": [
                    "application/json",
                    ],
                "produces": [
                    "application/json"
                    ],
                "responses": {
                    "200": {
                        "description": "successful operation",
                        "schema": {
                            "type": "array",
                            "items": {
                                "$ref": "#/definitions/role"
                            }
                        }
                    },
                    "401": {
                        "description": "Unauthorized"
                    }
                },
            },
        },
    }

    def reply(self):
        pmemb = getToolByName(aq_inner(self.context), "portal_membership")
        roles = [r for r in pmemb.getPortalRoles() if r != "Owner"]
        return [
            {
                "@type": "role",
                "@id": "{}/@roles/{}".format(self.context.absolute_url(), r),
                "id": r,
                "title": translate(r, context=self.request, domain="plone"),
            }
            for r in roles
        ]
