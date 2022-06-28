from zExceptions import BadRequest
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPublisher
from z3c.form import interfaces
from plone.restapi.interfaces import ISerializeToJson
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
