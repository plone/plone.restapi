# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.deserializer import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from zope.component import queryMultiAdapter


class DexterityGet(Service):

    def render(self):
        return ISerializeToJson(self.context)


class ContentPatch(Service):

    def render(self):
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
