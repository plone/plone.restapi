# -*- coding: utf-8 -*-

# pylint: disable=E0211, W0221
# E0211: Method has no argument
# W0221: Arguments number differs from overridden '__call__' method

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


class IJsonCompatible(Interface):
    """Convert a value to a JSON compatible data structure.
    """


class IFieldSerializer(Interface):
    """The field serializer multi adapter serializes the field value into
    JSON compatible python data.
    """

    def __init__(field, context, request):
        """Adapts field, context and request.
        """

    def __call__():
        """Returns JSON compatible python data.
        """


class IDeserializeFromJson(Interface):
    """An adapter to deserialize a JSON object into an object in Plone."""


class IFieldDeserializer(Interface):
    """An adapter to deserialize a JSON value into a field value.
    """

    def __init__(field, context, request):
        """Adapts a field, it's context and the request.
        """

    def __call__(value):
        """Convert the provided JSON value to a field value.
        """
