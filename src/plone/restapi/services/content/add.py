# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.app.content.interfaces import INameFromTitle
from plone.rest import Service
from plone.restapi.deserializer import DeserializationError
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from random import randint
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser

import transaction


class FolderPost(Service):
    """Creates a new content object.
    """

    def render(self):
        sm = getSecurityManager()
        if not sm.checkPermission('Add portal content', self.context):
            raise Unauthorized

        data = json_body(self.request)

        type_ = data.get('@type', None)
        id_ = data.get('id', None)
        title = data.get('title', None)

        if not type_:
            raise BadRequest("Property '@type' is required")

        # Generate a temporary id if the id is not given
        if not id_:
            now = DateTime()
            new_id = '%s.%s' % (now.millis(), randint(0, 99999999))
        else:
            new_id = id_

        # Create object
        try:
            new_id = self.context.invokeFactory(type_, new_id, title=title)
        except BadRequest as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='DeserializationError',
                message=str(e.message)))
        except ValueError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='DeserializationError',
                message=str(e.message)))

        # Update fields
        obj = self.context[new_id]
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
            chooser = INameChooser(self.context)
            # INameFromTitle adaptable objects should not get a name
            # suggestion. NameChooser would prefer the given name instead of
            # the one provided by the INameFromTitle adapter.
            name_from_title = INameFromTitle(obj, None)
            if name_from_title is None:
                name = chooser.chooseName(title, obj)
            else:
                name = chooser.chooseName(None, obj)
            transaction.savepoint(optimistic=True)
            self.context.manage_renameObject(new_id, name)

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', obj.absolute_url())
        return None
