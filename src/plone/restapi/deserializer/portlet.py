# -*- coding: utf-8 -*-
from plone.app.textfield.interfaces import IRichText
from plone.app.textfield.value import RichTextValue
from plone.portlets.interfaces import IPortletAssignmentSettings
from plone.portlets.interfaces import IPortletManager
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces import IRequest
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.services.portlets.utils import get_portletmanagers
from plone.restapi.services.portlets.utils import get_portlet_types
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.component import queryUtility
from zope.component.interfaces import IFactory
from zope.container import contained
from zope.container.interfaces import INameChooser
from zope.schema import getFields
from zope.schema.interfaces import IField
from zope.schema.interfaces import IFromUnicode
from zope.schema.interfaces import ValidationError
import six


@implementer(IDeserializeFromJson)
@adapter(Interface, IPortletManager, IRequest)
class DeserializePortletFromJson(object):
    """JSON deserializer for portlets
    """

    def __init__(self, context, manager, request):
        self.context = context
        self.manager = manager
        self.request = request
        self.portletmanagers = dict(get_portletmanagers())
        self.portlettypes = dict(get_portlet_types())

    def __call__(self, data=None):
        errors = []
        if data is None:
            data = json_body(self.request)

        portlet_type = data.get('@type', None)
        portlet_manager = data.get('manager', None)

        if portlet_manager not in self.portletmanagers:
            raise BadRequest("Invalid manager {}".format(portlet_manager))

        if portlet_type not in self.portlettypes:
            raise BadRequest("Invalid type {}".format(portlet_type))

        iface = self.portlettypes.get(portlet_type)
        fields = getFields(iface)
        portlet_data = dict()
        for field_name, field in fields.items():
            # Deserialize to field value
            deserializer = queryMultiAdapter(
                (field, self.request), IFieldDeserializer
            )
            if deserializer is None or field_name not in data:
                continue

            try:
                value = deserializer(data[field_name])
            except ValueError as e:
                errors.append({"message": str(e), "field": field_name, "error": e})
                continue
            except ValidationError as e:
                errors.append({"message": e.doc(), "field": field_name, "error": e})
                continue

            portlet_data[field_name] = value

        manager = queryMultiAdapter((self.context, self.manager), IPortletAssignmentMapping)
        factory = queryUtility(IFactory, name=portlet_type)
        if not factory:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message="Could not get factory for portlet type {}".format(portlet_type))
            )
        assignment = factory(**portlet_data)

        portlet_id = data.get('portlet_id', None)
        if portlet_id:
            # If portlet id is specified, check if there is a portlet with that id, and if so, remove it
            if portlet_id in manager:
                # set fixing_up to True to let zope.container.contained
                # know that our object doesn't have __name__ and __parent__
                fixing_up = contained.fixing_up
                contained.fixing_up = True
                del manager[portlet_id]
                # revert our fixing_up customization
                contained.fixing_up = fixing_up
        else:
            chooser = INameChooser(manager)
            portlet_id = chooser.chooseName(None, assignment)

        manager[portlet_id] = assignment

        visible = data.get('visible', True)
        settings = IPortletAssignmentSettings(assignment)
        settings['visible'] = visible


@implementer(IFieldDeserializer)
@adapter(IField, IBrowserRequest)
class DefaultGeneralFieldDeserializer(object):
    def __init__(self, field, request):
        self.field = field
        self.request = request

    def __call__(self, value):
        if not isinstance(value, six.text_type):
            self.field.validate(value)
            return value

        value = IFromUnicode(self.field).fromUnicode(value)
        # IFromUnicode.fromUnicode() will validate, no need to do it twice
        return value


@implementer(IFieldDeserializer)
@adapter(IRichText, IBrowserRequest)
class RichTextGeneralFieldDeserializer(DefaultGeneralFieldDeserializer):
    def __call__(self, value):
        content_type = self.field.default_mime_type
        encoding = "utf8"
        if isinstance(value, dict):
            content_type = value.get("content-type", content_type)
            encoding = value.get("encoding", encoding)
            data = value.get("data", u"")
        else:
            data = value

        value = RichTextValue(
            raw=data,
            mimeType=content_type,
            outputMimeType=self.field.output_mime_type,
            encoding=encoding,
        )
        self.field.validate(value)
        return value
