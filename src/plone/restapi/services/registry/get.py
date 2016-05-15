# -*- coding: utf-8 -*-
from plone.rest import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class RegistryGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(RegistryGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /_registry as parameters
        self.params.append(name)
        return self

    def render(self):
        return {'key': 'value'}
