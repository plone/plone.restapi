from collections import OrderedDict
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.services import Service
from plone.restapi.types.utils import add_field
from plone.restapi.types.utils import add_fieldset
from plone.restapi.types.utils import delete_field
from plone.restapi.types.utils import delete_fieldset
from plone.restapi.types.utils import get_info_for_type
from plone.restapi.types.utils import serializeSchema
from plone.restapi.types.utils import update_field
from plone.restapi.types.utils import update_fieldset
from plone.supermodel.interfaces import FIELDSETS_KEY
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import noLongerProvides
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces


@implementer(IPublishTraverse)
class TypesPut(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    def update_layouts(self, name, data):
        layouts = data.get("layouts", [])
        if not layouts:
            return

        ttool = getToolByName(self.context, "portal_types")
        ttool[name].view_methods = tuple(layouts)

    def remove_fieldsets(self, ctype, data):
        fieldsets = [f.get("id") for f in data.get("fieldsets", [])]
        existing = {
            f.__name__ for f in ctype.schema.queryTaggedValue(FIELDSETS_KEY, [])
        }

        for fieldset in existing:
            if fieldset not in fieldsets:
                delete_fieldset(ctype, self.request, fieldset)

    def add_fieldsets(self, ctype, data):
        fieldsets = OrderedDict((f.get("id"), f) for f in data.get("fieldsets", []))
        info = get_info_for_type(ctype, self.request, ctype.getId())
        existing = {f.get("id") for f in info.get("fieldsets", [])}
        for name, fieldset in fieldsets.items():
            if name not in existing:
                add_fieldset(ctype, self.request, fieldset)

    def remove_fields(self, ctype, data):
        fields = data.get("properties", {})
        existing = {name for name in ctype.schema}
        for name in existing:
            if name not in fields:
                delete_field(ctype, self.request, name)

    def add_fields(self, ctype, data):
        allow = [ctype.schema.__identifier__, ""]
        required = data.get("required", [])
        for name, field in data.get("properties", {}).items():
            if name in ctype.schema:
                continue

            behavior = field.get("behavior", "")
            if behavior not in allow:
                continue

            if name in required:
                field["required"] = True
            field["id"] = name
            add_field(ctype, self.request, field)

    def update_fieldsets(self, ctype, data):
        existing = {
            f.__name__ for f in ctype.schema.queryTaggedValue(FIELDSETS_KEY, [])
        }
        existing.add("default")
        for fieldset in data.get("fieldsets", []):
            if fieldset.get("id") not in existing:
                continue
            update_fieldset(ctype, self.request, fieldset)

    def update_fields(self, ctype, data):
        for name, field in data.get("properties", {}).items():
            if name not in ctype.schema:
                continue

            field["id"] = name
            update_field(ctype, self.request, field)

    def reply(self):
        if not self.params:
            raise BadRequest("Missing parameter typename")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        # Make sure we get the right dexterity-types adapter
        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        data = json_body(self.request)
        name = self.params.pop()
        dtypes = queryMultiAdapter((self.context, self.request), name="dexterity-types")
        ctype = dtypes.publishTraverse(self.request, name)

        self.update_layouts(name, data)
        self.remove_fields(ctype, data)
        self.remove_fieldsets(ctype, data)
        self.add_fields(ctype, data)
        self.add_fieldsets(ctype, data)
        self.update_fields(ctype, data)
        self.update_fieldsets(ctype, data)

        serializeSchema(ctype.schema)
        return self.reply_no_content()
