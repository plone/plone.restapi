# -*- coding: utf-8 -*-
from plone.restapi.services.types.get import TypesGet
from plone.restapi.types.utils import get_jsonschema_for_portal_type
from zExceptions import NotFound


class SchemaGet(TypesGet):

    def publishTraverse(self, request, name):
        # The @schema endpoint is not traversable (as oppsed to the @types
        # endpoint it inherits from)
        raise NotFound

    def reply(self):
        self.check_security()

        self.content_type = "application/json+schema"
        portal_type = self.context.portal_type
        return get_jsonschema_for_portal_type(
            portal_type, self.context, self.request
        )
