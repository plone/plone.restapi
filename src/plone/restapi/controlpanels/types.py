# -*- coding: utf-8 -*-
from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from plone.i18n.normalizer import idnormalizer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.deserializer import json_body
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.controlpanels.interfaces import IDexterityTypesControlpanel
import plone.protect.interfaces
from zope.interface import noLongerProvides
from plone.restapi.interfaces import IPloneRestapiLayer
from Products.CMFPlone.utils import getFSVersionTuple

PLONE5 = getFSVersionTuple()[0] >= 5


@adapter(Interface, IPloneRestapiLayer)
@implementer(IDexterityTypesControlpanel)
class DexterityTypesControlpanel(RegistryConfigletPanel):
    schema = Interface
    configlet_id = "dexterity-types"
    configlet_category_id = "plone-content" if PLONE5 else "Plone"

    def add(self, names):
        data = json_body(self.request)

        title = data.get("title", None)
        if not title:
            raise BadRequest("Property 'title' is required")

        tid = data.get("id", None)
        if not tid:
            tid = idnormalizer.normalize(title).replace("-", "_")

        description = data.get("description", "")

        properties = {"id": tid, "title": title, "description": description}

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        add_type = queryMultiAdapter((context, self.request), name="add-type")
        fti = add_type.form_instance.create(data=properties)
        add_type.form_instance.add(fti)
        return self.get([tid])

    def get(self, names):
        name = names[0]

        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)
        serializer = ISerializeToJson(self)
        return serializer(context)

    def update(self, names):
        name = names[0]

        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        context = context.publishTraverse(self.request, name)
        deserializer = IDeserializeFromJson(self)
        return deserializer(context)

    def delete(self, names):
        name = names[0]

        if IPloneRestapiLayer.providedBy(self.request):
            noLongerProvides(self.request, IPloneRestapiLayer)

        context = queryMultiAdapter(
            (self.context, self.request), name="dexterity-types"
        )
        edit = queryMultiAdapter((context, self.request), name="edit")
        edit.form_instance.remove((name, None))
