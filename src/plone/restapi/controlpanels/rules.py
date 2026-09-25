"""Control panel adapter for content rules (``@controlpanels/content-rules``)."""

from __future__ import annotations

from plone.restapi.controlpanels import RegistryConfigletPanel
from plone.restapi.controlpanels.interfaces import IContentRulesControlpanel
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IControlpanelLayer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.controlpanels.rules import rule_schema_as_json
from typing import Any
from typing import TYPE_CHECKING
from z3c.form import interfaces
from zExceptions import BadRequest
from zExceptions import NotFound
from zope.component import adapter
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.interface import Interface
from zope.publisher.interfaces.browser import IBrowserPublisher

import plone.protect.interfaces

if TYPE_CHECKING:
    from plone.autoform.form import AutoExtensibleForm
    from plone.contentrules.rule.interfaces import IRuleElementData
    from plone.contentrules.rule.rule import Rule
    from plone.z3cform.layout import FormWrapper
    from zope.publisher.interfaces.browser import IBrowserRequest


def include_fieldset_fields(form: AutoExtensibleForm) -> None:
    """Make the form's fields include the fields of all its fieldsets.

    ``plone.autoform`` puts fields declared in a non-default fieldset on
    ``form.groups``, and the rule element forms are not group forms, so
    ``applyChanges`` and ``form.fields`` would otherwise skip them.

    :param form: An updated :class:`plone.autoform.form.AutoExtensibleForm`.
    """
    fields = form.fields
    for group in form.groups:
        fields += group.fields
    form.fields = fields


@adapter(Interface, IControlpanelLayer)
@implementer(IContentRulesControlpanel, IBrowserPublisher)
class ContentRulesControlpanel(RegistryConfigletPanel):
    """Control panel to manage content rules and their conditions and actions.

    Each method receives ``names``, the path segments that follow
    ``@controlpanels/content-rules`` in the request URL:

    * ``[]`` — the control panel itself;
    * ``[rule_id]`` — a single rule;
    * ``[rule_id, category]`` — the conditions or actions of a rule,
      where ``category`` is ``"condition"`` or ``"action"``;
    * ``[rule_id, category, index]`` — a single condition or action.
    """

    configlet_id = "ContentRules"
    configlet_category_id = "plone-content"

    def publishTraverse(self, request: IBrowserRequest, name: str) -> Rule:
        """Traverse to a content rule.

        :param request: The current request.
        :param name: The id of the rule.
        :returns: The content rule.
        """
        return self.context.restrictedTraverse("++rule++" + name)

    def get_searchable_text(self) -> list[str]:
        """Return the texts used to find this control panel in a search.

        Extends the base texts with the titles of all registered rules.

        :returns: The searchable texts.
        """
        text_parts = super().get_searchable_text()

        cpanel = queryMultiAdapter(
            (self.context, self.request), name="rules-controlpanel"
        )
        if cpanel:
            registered_rules = cpanel.registeredRules()
            for rule in registered_rules:
                if isinstance(rule, dict) and rule.get("title"):
                    text_parts.append(rule["title"])

        return text_parts

    # Helpers

    def _get_view(self, rules: Any) -> FormWrapper:
        """Return the add form view for content rules.

        :param rules: The rule adding view (``+rule``).
        :returns: The ``plone.ContentRule`` form view.
        :raises NotFound: If the view is not registered.
        """
        view = queryMultiAdapter((rules, self.request), name="plone.ContentRule")
        if not view:
            raise NotFound("Rules control panel view could not be found")
        return view

    def _disable_csrf_protection(self) -> None:
        """Disable CSRF protection for the current request, when available."""
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

    def _get_manage_elements(self, rule: Rule) -> Any:
        """Return the ``manage-elements`` view of a rule, already authorized.

        :param rule: The content rule.
        :returns: The ``manage-elements`` view.
        """
        manage_elements = queryMultiAdapter(
            (rule, self.request), name="manage-elements"
        )
        manage_elements.authorize = lambda: True
        return manage_elements

    @staticmethod
    def _get_elements(rule: Rule, category: str) -> list[IRuleElementData]:
        """Return the conditions or actions of a rule.

        :param rule: The content rule.
        :param category: ``"condition"`` or ``"action"``.
        :returns: The rule's conditions or actions.
        """
        return getattr(rule, f"{category}s")

    def _get_edit_form(self, element: IRuleElementData) -> AutoExtensibleForm | None:
        """Return the updated edit form of a condition or action.

        :param element: The condition or action.
        :returns: The edit form, including the fields of all its fieldsets,
            or ``None`` if the element has no edit view.
        """
        view = queryMultiAdapter((element, self.request), name="edit")
        if not view:
            return None
        form = view.form_instance
        form.update()
        include_fieldset_fields(form)
        return form

    # Add

    def add(self, names: list[str]) -> dict[str, Any]:
        """Add a rule, or a condition or action to an existing rule.

        The values come from the JSON body of the request. To add a
        condition or action, the body must contain its ``type``: the name
        of the element's add view, for example ``plone.actions.Notify``.

        :param names: ``[]`` to add a rule, or ``[rule_id, category]`` to add
            a condition or action to that rule.
        :returns: The serialized rule.
        :raises BadRequest: If the rule ``title`` or the element ``type`` is
            missing, or if only the rule id is given.
        :raises NotFound: If there is no add view for the requested type.
        """
        data = json_body(self.request)
        if not names:
            rule = self._add_rule(data)
        elif len(names) == 1:
            raise BadRequest("Rule id and condition or action are required")
        else:
            rule = self._add_element(names[0], names[1], data)
        return self.get([rule.__name__])

    def _add_rule(self, data: dict[str, Any]) -> Rule:
        """Create a content rule.

        :param data: The rule values; ``event`` is the title of the event.
        :returns: The new rule.
        :raises BadRequest: If ``title`` is missing.
        """
        rules = queryMultiAdapter((self.context, self.request), name="+rule")
        form = self._get_view(rules).form_instance
        form.update()
        if not data.get("title"):
            raise BadRequest("Property 'title' is required")
        widget = form.widgets["event"]
        data["event"] = interfaces.IDataConverter(widget).toFieldValue([data["event"]])
        self._disable_csrf_protection()
        rule = form.create(data)
        form.add(rule)
        return rule

    def _add_element(self, rule_id: str, category: str, data: dict[str, Any]) -> Rule:
        """Add a condition or action to a rule.

        :param rule_id: The id of the rule.
        :param category: ``"condition"`` or ``"action"``.
        :param data: The element values, including its ``type``.
        :returns: The rule.
        :raises BadRequest: If ``type`` is missing.
        :raises NotFound: If there is no add view for the requested type.
        """
        try:
            view_name = data.pop("type")
        except KeyError:
            raise BadRequest(f"{category.title()} type is required")
        rule = self.publishTraverse(self.request, name=rule_id)
        adding = self.context.restrictedTraverse(f"++rule++{rule_id}/+{category}")
        view = queryMultiAdapter((adding, self.request), name=view_name)
        if not view:
            raise NotFound(f"View '{view_name}' could not be found for {category}")
        self._disable_csrf_protection()
        if view_name == "plone.actions.Delete":
            # The delete action has no form: its view adds it directly
            view()
        else:
            form = view.form_instance
            form.update()
            include_fieldset_fields(form)
            form.add(form.create(data))
        return rule

    # Get

    def get(self, names: list[str]) -> dict[str, Any] | None:
        """Serialize a rule, or one of its conditions or actions.

        :param names: ``[rule_id]`` for a rule, or
            ``[rule_id, category, index]`` for a condition or action.
        :returns: The serialized rule; or the values of the condition or
            action, with its ``@id`` and ``@schema``. ``None`` if the
            condition or action has no edit view, and so no values to show.
        """
        if len(names) == 1:
            rule = self.publishTraverse(self.request, names[0])
            return ISerializeToJson(self)(rule)
        return self._serialize_element(names[0], names[1], int(names[2]))

    def _serialize_element(
        self, rule_id: str, category: str, idx: int
    ) -> dict[str, Any] | None:
        """Serialize a condition or action of a rule.

        :param rule_id: The id of the rule.
        :param category: ``"condition"`` or ``"action"``.
        :param idx: The position of the element in the rule.
        :returns: The element values, with its ``@id`` and ``@schema``, or
            ``None`` if the element has no edit view.
        """
        rule = self.publishTraverse(self.request, name=rule_id)
        element = self._get_elements(rule, category)[idx]
        form = self._get_edit_form(element)
        if form is None:
            return None
        base_url = f"{self.context.absolute_url()}/@controlpanels/content-rules"
        result: dict[str, Any] = {"@id": f"{base_url}/{rule_id}/{category}/{idx}"}
        for name in form.fields:
            result[name] = getattr(element, name)
        result["@schema"] = rule_schema_as_json(form.schema, self.request)
        return result

    # Update

    def update(self, names: list[str]) -> None:
        """Update a rule, or one of its conditions or actions.

        The values come from the JSON body of the request. For a rule, the
        body may contain ``form.button.ApplyOnWholeSite`` to assign it to the
        whole site. For a condition or action, it may contain
        ``form.button.Move`` with the name of a move method of the
        ``manage-elements`` view, for example ``_move_up``.

        :param names: ``[rule_id]`` for a rule, or
            ``[rule_id, category, index]`` for a condition or action.
        :raises BadRequest: If the index of the condition or action is
            missing.
        """
        data = json_body(self.request)
        rule = self.publishTraverse(self.request, name=names[0])
        if len(names) == 1:
            self._update_rule(rule, data)
            return
        if len(names) == 2:
            raise BadRequest(f"{names[1].title()} and its index are required")
        elements = self._get_elements(rule, names[1])
        idx = int(names[2])
        move_action = data.get("form.button.Move")
        if move_action:
            manage_elements = self._get_manage_elements(rule)
            getattr(manage_elements, move_action)(elements, idx)
        else:
            self._get_edit_form(elements[idx]).applyChanges(data)

    def _update_rule(self, rule: Rule, data: dict[str, Any]) -> None:
        """Update the settings of a rule, or assign it to the whole site.

        :param rule: The content rule.
        :param data: The new values.
        """
        if "form.button.ApplyOnWholeSite" in data:
            self._get_manage_elements(rule).globally_assign()
            return
        rule.title = data.get("title", rule.title)
        rule.description = data.get("description", rule.description)
        rule.stop = data.get("stopExecuting", False)
        rule.cascading = data.get("cascading", False)
        rule.enabled = data.get("enabled", False)

    # Delete

    def delete(self, names: list[str]) -> None:
        """Delete a rule, or one of its conditions or actions.

        :param names: ``[rule_id]`` for a rule, or
            ``[rule_id, category, index]`` for a condition or action.
        :raises BadRequest: If the index of the condition or action is
            missing.
        """
        if len(names) == 1:
            self._delete_rule(names[0])
            return
        category = names[1]
        if len(names) == 2:
            raise BadRequest(f"{category.title()} index is required")
        rule = self.publishTraverse(self.request, name=names[0])
        del self._get_elements(rule, category)[int(names[2])]

    def _delete_rule(self, rule_id: str) -> None:
        """Delete a content rule.

        :param rule_id: The id of the rule.
        """
        self.request["rule-id"] = rule_id
        cpanel = queryMultiAdapter(
            (self.context, self.request), name="rules-controlpanel"
        )
        # Disable CSRF protection
        # The "regular" way to force authorization was via the interface
        # IDisableCSRFProtection, but the plone.app.contentrules controlpanel
        # calls authorize directly, so we need to override that here
        cpanel.authorize = lambda: True
        cpanel.delete_rule()
