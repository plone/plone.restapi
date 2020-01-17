# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from plone.restapi.services.portlets.utils import get_portletmanagers
from plone.restapi.services.portlets.utils import manager_by_name
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class PortletsGet(Service):
    portletmanager_id = None

    def publishTraverse(self, request, name):  # noqa
        if name:
            self.portletmanager_id = name
        return self

    def reply(self):
        if self.portletmanager_id:
            return self.reply_portletmanager()

        def serialize(portletmanagers):
            for name, manager in portletmanagers:
                serializer = queryMultiAdapter(
                   (manager, self.context, self.request),
                   ISerializeToJsonSummary)
                yield serializer()

        portletmanagers = get_portletmanagers()
        return IJsonCompatible(list(serialize(portletmanagers)))

    def reply_portletmanager(self):
        manager = manager_by_name(self.context, self.portletmanager_id)
        if manager is None:
            self.request.response.setStatus(404)
            return
        serializer = queryMultiAdapter((manager, self.context, self.request),
                                       ISerializeToJson)
        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message='No serializer available.'))
        return serializer()
