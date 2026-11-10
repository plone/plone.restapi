from plone.restapi.services.workflows import WorkflowsService
from plone.restapi.typesettings.workflows import visibility
from Products.CMFCore.interfaces import IWorkflowDefinition
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from zope.i18n import translate


class WorkflowsGet(WorkflowsService):
    """The workflows that can be assigned to content types."""

    def reply(self):
        if self.params:
            return self.serialize_full(self.get_workflow())
        workflows = [
            self.serialize(workflow)
            for workflow in self.workflow_tool.objectValues()
            if IWorkflowDefinition.providedBy(workflow)
        ]
        default = self.workflow_tool.getDefaultChain()
        return {
            "@id": self.url(),
            "default": default[0] if default else None,
            "items": sorted(workflows, key=lambda item: (item["title"], item["id"])),
        }

    def get_workflow(self):
        workflow = None
        if len(self.params) == 1:
            workflow = self.workflow_tool.getWorkflowById(self.params[0])
        if workflow is None:
            raise NotFound("Unknown workflow")
        return workflow

    def translate(self, text):
        return translate(text or "", domain="plone", context=self.request)

    def serialize(self, workflow):
        return {
            "@id": self.url(workflow.getId()),
            "id": workflow.getId(),
            "title": self.translate(workflow.title),
            "description": self.translate(workflow.description),
            "initial_state": workflow.initial_state,
            "states": list(workflow.states.objectIds()),
        }

    def serialize_full(self, workflow):
        result = self.serialize(workflow)
        result["states"] = [
            {
                "id": state.getId(),
                "title": self.translate(state.title),
                "description": self.translate(state.description),
                "transitions": list(state.transitions),
                "visibility": visibility(state),
                "permission_roles": {
                    permission: list(roles)
                    for permission, roles in (state.permission_roles or {}).items()
                },
            }
            for state in workflow.states.objectValues()
        ]
        result["transitions"] = [
            {
                "id": transition.getId(),
                # The action title, as in @workflow, like "Publish".
                "title": self.translate(transition.actbox_name or transition.title),
                "description": self.translate(transition.description),
                "new_state": transition.new_state_id,
                "guard": self.serialize_guard(transition.guard),
            }
            for transition in workflow.transitions.objectValues()
        ]
        result["types"] = self.types(workflow.getId())
        return result

    def serialize_guard(self, guard):
        if guard is None:
            return {"permissions": [], "roles": [], "expression": ""}
        return {
            "permissions": list(guard.permissions or ()),
            "roles": list(guard.roles or ()),
            "expression": guard.getExprText(),
        }

    def types(self, workflow_id):
        """The types whose chain has the workflow, also through the default."""
        types_tool = getToolByName(self.context, "portal_types")
        return sorted(
            type_id
            for type_id in types_tool.listContentTypes()
            if workflow_id in self.workflow_tool.getChainFor(type_id)
        )
