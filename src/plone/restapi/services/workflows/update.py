from plone.restapi.services.workflows import WorkflowsService
from plone.restapi.typesettings.workflows import apply_change
from plone.restapi.typesettings.workflows import check_state_map
from plone.restapi.typesettings.workflows import DEFAULT_CHAIN
from plone.restapi.typesettings.workflows import get_workflow
from plone.restapi.typesettings.workflows import plan_change
from plone.restapi.typesettings.workflows import workflow_id
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.controlpanel.events import ConfigurationChangedEvent
from zExceptions import BadRequest
from zope.event import notify


class WorkflowsPost(WorkflowsService):
    """Change the default workflow, and the states of items of the types
    following it."""

    def reply(self):
        if self.params:
            raise BadRequest(f"Change the default workflow at {self.url()}")
        body = self.json_body()
        workflow_tool = self.workflow_tool
        if "default" not in body:
            self.raise_errors(
                [{"field": "default", "message": "Expected a workflow", "error": None}]
            )
        new_id = body["default"]
        if new_id is not None and (
            not isinstance(new_id, str) or workflow_tool.getWorkflowById(new_id) is None
        ):
            self.raise_errors(
                [{"field": "default", "message": "Unknown workflow", "error": None}]
            )
        chain = (new_id,) if new_id else ()
        old_chain = tuple(workflow_tool.getDefaultChain())
        current = get_workflow(self.context, old_chain)
        target = get_workflow(self.context, chain)
        errors = check_state_map(body.get("state_map"), target)
        if errors:
            self.raise_errors(errors)

        overrides = dict(workflow_tool.listChainOverrides())
        types_tool = getToolByName(self.context, "portal_types")
        type_ids = sorted(
            type_id
            for type_id in types_tool.listContentTypes()
            if type_id not in overrides
        )
        if body.get("dry_run"):
            return {
                "workflow": new_id,
                "current": workflow_id(current),
                **plan_change(self.context, type_ids, current, target),
                "types": type_ids,
            }

        changed = 0
        if workflow_id(current) == workflow_id(target):
            workflow_tool.setDefaultChain(",".join(chain))
        else:
            # Like the classic form: keep the old chain while the default
            # changes, so the remapping knows the states of the old one.
            workflow_tool.setChainForPortalTypes(type_ids, old_chain)
            workflow_tool.setDefaultChain(",".join(chain))
            changed = apply_change(
                self.context,
                type_ids,
                DEFAULT_CHAIN,
                current,
                target,
                body.get("state_map"),
            )
        notify(ConfigurationChangedEvent(self, {"workflow": new_id}))
        return {"default": new_id, "changed": changed}
