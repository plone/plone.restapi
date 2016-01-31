# -*- coding: utf-8 -*-
from AccessControl import Unauthorized
from AccessControl import getSecurityManager
from DateTime import DateTime
from plone.rest import Service
from plone.restapi.deserializer import DeserializationError
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from random import randint
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.container.interfaces import INameChooser

import transaction


class DexterityGet(Service):

    def render(self):
        return ISerializeToJson(self.context)


class ContentPatch(Service):

    def render(self):
        sm = getSecurityManager()
        if not sm.checkPermission('Modify portal content', self.context):
            raise Unauthorized

        deserializer = queryMultiAdapter((self.context, self.request),
                                         IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(
                message='Cannot deserialize type {}'.format(
                    self.context.portal_type)))

        try:
            deserializer()
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='DeserializationError',
                message=str(e)))

        # TODO: alternativley return the patched object with a 200
        self.request.response.setStatus(204)
        return None


class FolderPost(Service):
    """Creates a new object.
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
            name = chooser.chooseName(title, obj)
            transaction.savepoint(optimistic=True)
            self.context.manage_renameObject(new_id, name)

        self.request.response.setStatus(201)
        self.request.response.setHeader('Location', obj.absolute_url())
        return None

# class DexterityPost(Service):
#
#     def render(self):
#         return {'service': 'post'}


# class DexterityPut(Service):
#
#     def render(self):
#         return {'service': 'put'}


# class DexterityDelete(Service):
#
#     def render(self):
#         return {'service': 'delete'}


class PloneSiteRootGet(Service):

    def render(self):
        return ISerializeToJson(self.context)


# class PloneSiteRootPost(Service):
#
#     def render(self):
#         return {'service': 'options'}
