# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.interfaces import ISerializeToJson
from zope.component import queryAdapter


class DefaultGetService(Service):
    def render(self):
        frame = self.request.get('frame', 'content')
        adapter = queryAdapter(
            self.context,
            interface=ISerializeToJson,
            name=frame,
            default={})
        if callable(adapter):
            result = adapter()
        else:
            result = adapter
        return result


class DexterityGet(DefaultGetService):
    """ Default Dexterity Get
    """


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


class PloneSiteRootGet(DefaultGetService):
    """ Default Plone Get
    """


# class PloneSiteRootPost(Service):
#
#     def render(self):
#         return {'service': 'options'}
