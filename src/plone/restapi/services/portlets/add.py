# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import IJsonCompatible
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.portlets.utils import get_portletmanagers
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
import plone.protect.interfaces


class PortletPost(Service):
    """Creates portlet in context.
    """

    def reply(self):
        data = json_body(self.request)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        portletmanagers = dict(get_portletmanagers())

        portlet_type = data.get('@type', None)
        portlet_manager = data.get('manager', None)

        if not (portlet_manager or portlet_type):
            raise BadRequest(
                "'@type', and 'manager' are required properties for a portlet to be added")

        if portlet_manager not in portletmanagers:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message="Invalid manager {}".format(portlet_manager))
            )

        pm = portletmanagers.get(portlet_manager)

        # Create portlet
        deserializer = queryMultiAdapter((self.context, pm, self.request), IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message="Cannot deserialize portlet for manager {}".format(portlet_manager))
            )

        try:
            deserializer(data)
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        results = list()
        for name, manager in portletmanagers.items():
            serializer = queryMultiAdapter(
                (manager, self.context, self.request),
                ISerializeToJson)
            results.append(serializer())

        return IJsonCompatible(results)
