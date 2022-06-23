from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.controlpanels.interfaces import IContentRulesControlpanel
from zope.publisher.interfaces.browser import IBrowserPublisher
from zope.interface import noLongerProvides
import plone.protect.interfaces
from plone.restapi.interfaces import IPloneRestapiLayer


@adapter(Interface, IPloneRestapiLayer)
@implementer(IContentRulesControlpanel, IBrowserPublisher)
class ContentRulesControlpanel(RegistryConfigletPanel):
    schema = Interface
    configlet_id = "ContentRules"
    configlet_category_id = "plone-content"

    def publishTraverse(self, request, name):

        return self.context.restrictedTraverse("++rule++" + name)

    # def add(self, names):
    #     data = json_body(self.request)

    #     title = data.get("title", None)
    #     if not title:
    #         raise BadRequest("Property 'title' is required")

    #     tid = data.get("id", None)
    #     if not tid:
    #         tid = idnormalizer.normalize(title).replace("-", "_")

    #     description = data.get("description", "")

    #     properties = {"id": tid, "title": title, "description": description}

    #     # Disable CSRF protection
    #     if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
    #         alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

    #     #if IPloneRestapiLayer.providedBy(self.request):
    #     #    noLongerProvides(self.request, IPloneRestapiLayer)

    #     context = queryMultiAdapter(
    #         (self.context, self.request), name="content-rules"
    #     )
    #     add_type = queryMultiAdapter((context, self.request), name="add-type")
    #     fti = add_type.form_instance.create(data=properties)
    #     add_type.form_instance.add(fti)
    #     return self.get([tid])

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
        self.request['rule-id'] = name

        cpanel = queryMultiAdapter(
            (self.context, self.request), name="rules-controlpanel"
        )
        # Disable CSRF protection
        # The "regular" way to force authorization was via the interface
        # IDisableCSRFProtection, but the plone.app.contentrules controlpanel
        # calls authorize directly, so we need to override that here
        cpanel.authorize = lambda: True
        cpanel.delete_rule()
