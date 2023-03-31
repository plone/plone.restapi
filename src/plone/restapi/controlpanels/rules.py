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
from plone.restapi.serializer.controlpanels.rules import rule_schema_as_json
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
        if len(names) == 0:
            view = queryMultiAdapter((rules, self.request), name="plone.ContentRule")
            form = view.form_instance
            form.update()
            title = data.get("title", None)
            if not title:
                raise BadRequest("Property 'title' is required")
            widget = form.widgets["event"]
            data["event"] = interfaces.IDataConverter(widget).toFieldValue(
                [data["event"]]
            )
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )
            rule = form.create(data)
            form.add(rule)
        elif len(names) == 1:
            raise BadRequest("Rule id and condition or action are required")
        else:
            # we need to add a condition or action to the current rule
            name = names[0]
            extra = names[1]
            try:
                view_name = data.pop("type")
            except KeyError:
                raise BadRequest("%s type is required" % extra.title())
            rule = self.publishTraverse(self.request, name=name)
            extra_ob = self.context.restrictedTraverse(
                "++rule++" + name + "/+%s" % extra
            )
            view = queryMultiAdapter((extra_ob, self.request), name=view_name)
            if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
                alsoProvides(
                    self.request, plone.protect.interfaces.IDisableCSRFProtection
                )
            if view_name == "plone.actions.Delete":
                view()
            else:
                form = view.form_instance
                form.update()
                extra_ob = form.create(data)
                form.add(extra_ob)
        return self.get([rule.__name__])

    def get(self, names):
        if len(names) == 1:
            context = self.publishTraverse(self.request, names[0])
            serializer = ISerializeToJson(self)

            return serializer(context)
        else:
            # the get is for a condition or action
            rule_name = names[0]
            category = names[1]
            rule = self.publishTraverse(self.request, name=rule_name)
            extras = getattr(rule, f"{category}s")
            idx = int(names[2])
            extra_ob = extras[idx]
            view = queryMultiAdapter((extra_ob, self.request), name="edit")
            base_url = f"{self.context.absolute_url()}/@controlpanels/content-rules"
            fields = {"@id": f"{base_url}/{rule_name}/{category}/{idx}"}
            if view:
                view.form_instance.update()
                for field in view.form_instance.fields:
                    fields[field] = getattr(extra_ob, field)
                schema = view.form.schema
                fields["@schema"] = rule_schema_as_json(schema, self.request)
                return fields

    def update(self, names):
        data = json_body(self.request)
        name = names[0]
        rule = self.publishTraverse(self.request, name=name)
        manage_elements = queryMultiAdapter(
            (rule, self.request), name="manage-elements"
        )
        manage_elements.authorize = lambda: True
        move_action = data.get("form.button.Move")
        if len(names) == 1:
            # we are editing the rule
            if "form.button.ApplyOnWholeSite" in data:
                manage_elements.globally_assign()
            else:
                rule.title = data.get("title", rule.title)
                rule.description = data.get("description", rule.description)
                rule.stop = data.get("stopExecuting", False)
                rule.cascading = data.get("cascading", False)
                rule.enabled = data.get("enabled", False)
        elif len(names) == 2:
            raise BadRequest("%s and its index are required" % names[1].title())
        # we are editing a condition or action
        elif move_action:
            extras = getattr(rule, names[1] + "s")
            move_action = getattr(manage_elements, move_action)
            move_action(extras, int(names[2]))
        else:
            extras = getattr(rule, names[1] + "s")
            idx = int(names[2])
            extra_ob = extras[idx]
            view = queryMultiAdapter((extra_ob, self.request), name="edit")
            view.form_instance.update()
            view.form_instance.applyChanges(data)

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
            extra = names[1]
            if len(names) == 2:
                raise BadRequest("%s index is required" % extra.title())
            rule = self.publishTraverse(self.request, name=names[0])
            extras = getattr(rule, extra + "s")
            del extras[int(names[2])]
