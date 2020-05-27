# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.types.get import check_security
from plone.restapi.types.utils import create_fields
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


@implementer(IPublishTraverse)
class TypesPost(Service):
    """ Creates a new field/fieldset
    """
    def __init__(self, context, request):
        super(TypesPost, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def reply(self):
        if self.params and len(self.params) > 0:
            check_security(self.context)

            # Disable CSRF protection
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

            data = json_body(self.request)

            try:
                ptype = self.params.pop()
                return create_fields(self.context, self.request, data, ptype)
            except KeyError:
                self.content_type = "application/json"
                self.request.response.setStatus(404)
                return {
                    "type": "NotFound",
                    "message": 'Type "{}" could not be found.'.format(ptype),
                }

        return self.reply_no_content()
