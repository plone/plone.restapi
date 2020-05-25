# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.types.utils import create_fields
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
import plone.protect.interfaces


class TypesPost(Service):
    """ Creates a new field/fieldset
    """
    params = []

    def reply(self):
        data = json_body(self.request)

        portal_type = data.get('portal_type', None)
        if portal_type:
            # Disable CSRF protection
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
            import pdb; pdb.set_trace()
            create_fields(portal_type, self.context, self.request, data)
