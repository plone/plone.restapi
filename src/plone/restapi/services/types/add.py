# -*- coding: utf-8 -*-
from plone.i18n.normalizer import idnormalizer
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.types.utils import get_jsonschema_for_portal_type
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import alsoProvides

import plone.protect.interfaces


class TypesPost(Service):
    """ Creates a new content type.
    """

    def reply(self):
        portal = getSite()
        data = json_body(self.request)

        title = data.get("title", None)
        if not title:
            raise BadRequest("Property 'title' is required")

        tid = data.get("id", None)
        if not tid:
            tid = idnormalizer.normalize(title).replace("-", "_")

        description = data.get("description", "")

        properties = {
            "id": tid,
            "title": title,
            "description": description
        }

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        context = queryMultiAdapter((self.context, self.request), name='dexterity-types')
        add_type = queryMultiAdapter((context, self.request), name='add-type')
        fti = add_type.form_instance.create(data=properties)
        add_type.form_instance.add(fti)

        self.request.response.setStatus(201)
        self.request.response.setHeader(
            "Location", portal.absolute_url() + "/@types/" + tid
        )
        return get_jsonschema_for_portal_type(tid, self.context, self.request)
