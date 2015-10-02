# -*- coding: utf-8 -*-
from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IPloneRestapiLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IAPIRequest(Interface):
    """Marker for API requests.
    """


class ISerializeToJson(Interface):
    """Adapter to serialize a Dexterity object into a JSON object.
    """


class IContext(Interface):
    """Adapter to get the context of JSON-LD on a context
    """
