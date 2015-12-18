# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.interfaces import ISerializeToJson


class DexterityGet(Service):

    def render(self):
        return ISerializeToJson(self.context)


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


class ArchetypesGet(Service):
    def render(self):
        return ISerializeToJson(self.context)
