# -*- coding: utf-8 -*-
from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from Products.CMFPlone.utils import safe_hasattr
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent

import plone.protect.interfaces


class FolderPost(Service):
    """Creates a new content object.
    """

    def reply(self):
        data = json_body(self.request)

        type_ = data.get("@type", None)
        id_ = data.get("id", None)
        title = data.get("title", None)

        if not type_:
            raise BadRequest("Property '@type' is required")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        try:
            obj = create(self.context, type_, id_=id_, title=title)
        except Unauthorized as exc:
            self.request.response.setStatus(403)
            return dict(error=dict(type="Forbidden", message=str(exc)))
        except BadRequest as exc:
            self.request.response.setStatus(400)
            return dict(error=dict(type="Bad Request", message=str(exc)))

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        temporarily_wrapped = False
        if IAcquirer.providedBy(obj) and not safe_hasattr(obj, "aq_base"):
            obj = obj.__of__(self.context)
            temporarily_wrapped = True

        # Update fields
        deserializer = queryMultiAdapter((obj, self.request), IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message="Cannot deserialize type {}".format(obj.portal_type))
            )

        try:
            deserializer(validate_all=True, create=True)
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        if temporarily_wrapped:
            obj = aq_base(obj)

        if not getattr(deserializer, "notifies_create", False):
            notify(ObjectCreatedEvent(obj))

        obj = add(self.context, obj, rename=not bool(id_))

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", obj.absolute_url())

        serializer = queryMultiAdapter((obj, self.request), ISerializeToJson)

        serialized_obj = serializer()

        # HypermediaBatch can't determine the correct canonical URL for
        # objects that have just been created via POST - so we make sure
        # to set it here
        serialized_obj["@id"] = obj.absolute_url()

        return serialized_obj
