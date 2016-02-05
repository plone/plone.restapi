# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.interfaces import ISerializeToJson


class DexterityGet(Service):

    def render(self):
        return ISerializeToJson(self.context)


class PloneSiteRootGet(Service):

    def render(self):
        return ISerializeToJson(self.context)
