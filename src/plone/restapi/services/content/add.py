# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.content.utils import create
from plone.restapi.services.content.utils import rename
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides

import plone.protect.interfaces


class FolderPost(Service):
    """Creates a new content object.
    """

    def reply(self):
        data = json_body(self.request)

        type_ = data.get('@type', None)
        id_ = data.get('id', None)
        title = data.get('title', None)

        if not type_:
            raise BadRequest("Property '@type' is required")

        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        obj = create(self.context, type_, id_=id_, title=title)
        if isinstance(obj, dict) and 'error' in obj:
            self.request.response.setStatus(400)
            return obj

        # Update fields
        deserializer = queryMultiAdapter((obj, self.request),
                                         IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                message='Cannot deserialize type {}'.format(obj.portal_type)))

        try:
            deserializer(validate_all=True)
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='DeserializationError',
                message=str(e)))

        # Rename if generated id
        if not id_:
            rename(obj)

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', obj.absolute_url())

        serializer = queryMultiAdapter(
            (obj, self.request),
            ISerializeToJson
        )

        serialized_obj = serializer()

        # HypermediaBatch can't determine the correct canonical URL for
        # objects that have just been created via POST - so we make sure
        # to set it here
        serialized_obj['@id'] = obj.absolute_url()

        return serialized_obj
