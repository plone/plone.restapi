from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPublisher
from z3c.form import interfaces
from plone.restapi.interfaces import ISerializeToJson, IDeserializeFromJson
from plone.restapi.interfaces import IPloneRestapiLayer
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.controlpanels.interfaces import IContentRulesControlpanel
from plone.restapi.deserializer import json_body
import plone.protect.interfaces


@adapter(Interface, IPloneRestapiLayer)
@implementer(IContentRulesControlpanel, IBrowserPublisher)
class ContentRulesControlpanel(RegistryConfigletPanel):
    schema = Interface
    configlet_id = "ContentRules"
    configlet_category_id = "plone-content"

    def publishTraverse(self, request, name):

        return self.context.restrictedTraverse("++rule++" + name)

    def add(self, names):
        data = json_body(self.request)
        rules = queryMultiAdapter((self.context, self.request), name="+rule")
        if len(names) == 1:
            view = queryMultiAdapter((rules, self.request), name="plone.ContentRule")
            form = view.form_instance
            form.update()
            title = data.get("title", None)
            if not title:
                raise BadRequest("Property 'title' is required")
            widget = form.widgets["event"]
            data["event"] = interfaces.IDataConverter(widget).toFieldValue([data["event"]])
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
            rule = form.create(data)
            form.add(rule)
        else:
            # we need to add a condition or action to the current rule
            if len(names) == 2:
                raise BadRequest("%s type is required" % extra.title())
            extra =  names[1]
            rule = self.publishTraverse(self.request, name=names[0])
            view_name = names[2]
            extra_ob = self.context.restrictedTraverse(
                "++rule++" + names[0] + "/+%s" % extra
            )
            view = queryMultiAdapter((extra_ob, self.request), name=view_name)
            form = view.form_instance
            form.update()
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
            extra_ob = form.create(data)
            form.add(extra_ob)
        return self.get([rule.__name__])

    def get(self, names):
        name = names[0]

        context = self.publishTraverse(self.request, name)
        serializer = ISerializeToJson(self)

        return serializer(context)

    # def update(self, names):
    #     name = names[0]

    #     #if IPloneRestapiLayer.providedBy(self.request):
    #     #    noLongerProvides(self.request, IPloneRestapiLayer)

    #     context = queryMultiAdapter(
    #         (self.context, self.request), name="content-rules"
    #     )
    #     context = context.publishTraverse(self.request, name)
    #     deserializer = IDeserializeFromJson(self)
    #     return deserializer(context)

    def delete(self, names):
        if len(names) == 1:
            name = names[0]
            self.request["rule-id"] = name

            cpanel = queryMultiAdapter(
                (self.context, self.request), name="rules-controlpanel"
            )
            # Disable CSRF protection
            # The "regular" way to force authorization was via the interface
            # IDisableCSRFProtection, but the plone.app.contentrules controlpanel
            # calls authorize directly, so we need to override that here
            cpanel.authorize = lambda: True
            cpanel.delete_rule()
        else:
            # we need to delete a condition or action from the current rule
            if len(names) == 2:
                raise BadRequest("%s index is required" % extra.title())
            extra =  names[1]
            rule = self.publishTraverse(self.request, name=names[0])
            extras = getattr(rule, extra)
            del extras[int(names[2])]
