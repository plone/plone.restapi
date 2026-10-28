from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer
from plone.restapi.services.contenttypes import ContentTypesService
from plone.restapi.services.contenttypes import WORKFLOW
from plone.restapi.types.utils import _deserialize_schema_values
from plone.restapi.typesettings.interfaces import ITypeCreation
from plone.restapi.typesettings.manage import copy_type
from plone.restapi.typesettings.manage import create_type
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


class ContentTypesPost(ContentTypesService):
    def reply(self):
        if self.params[1:] == [WORKFLOW]:
            return self.change_workflow(self.get_fti(WORKFLOW))
        if self.params:
            raise BadRequest(f"Create content types at {self.url()}")
        body, errors = _deserialize_schema_values(
            self.context,
            self.request,
            ITypeCreation,
            self.json_body(),
            partial=False,
            strict=True,
        )
        if errors:
            self.raise_errors(errors)
        type_id = body.get("id") or idnormalizer.normalize(body["title"]).replace(
            "-", "_"
        )
        if type_id in self.types_tool:
            self.request.response.setStatus(409)
            return {
                "error": {
                    "type": "Conflict",
                    "message": "A content type with this ID already exists",
                }
            }
        self.check_id(type_id)
        if body.get("copy_from"):
            source = self.types_tool.get(body["copy_from"])
            if not IDexterityFTI.providedBy(source):
                self.raise_errors(
                    [
                        {
                            "field": "copy_from",
                            "message": "Expected the ID of a Dexterity content type",
                            "error": None,
                        }
                    ]
                )
            fti = copy_type(
                self.types_tool,
                source,
                type_id,
                body["title"],
                body.get("description"),
                self.request,
            )
        else:
            fti = create_type(
                self.types_tool, type_id, body["title"], body.get("description")
            )
        result = self.serialize(fti)
        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", result["@id"])
        return result

    def check_id(self, type_id):
        """Apply the ID rules of the types tool, like reserved names."""
        error = None
        if not type_id or "/" in type_id:
            error = "Invalid content type ID"
        else:
            try:
                self.types_tool._checkId(type_id)
            except BadRequest as exc:
                error = str(exc)
        if error:
            self.raise_errors([{"field": "id", "message": error, "error": None}])

    def change_workflow(self, fti):
        """Assign a workflow to the type, or plan it with ``dry_run``."""
        body = self.json_body()
        if not isinstance(body, dict):
            self.raise_errors([{"message": "Expected an object", "error": None}])
        workflow_tool = getToolByName(self.context, "portal_workflow")
        if body.get("follows_default"):
            chain = DEFAULT_CHAIN
            target_chain = workflow_tool.getDefaultChain()
        elif "workflow" in body:
            new_id = body["workflow"]
            if new_id is not None and (
                not isinstance(new_id, str)
                or workflow_tool.getWorkflowById(new_id) is None
            ):
                self.raise_errors(
                    [
                        {
                            "field": "workflow",
                            "message": "Unknown workflow",
                            "error": None,
                        }
                    ]
                )
            chain = target_chain = (new_id,) if new_id else ()
        else:
            self.raise_errors(
                [
                    {
                        "message": "Expected a workflow or follows_default",
                        "error": None,
                    }
                ]
            )
        type_id = fti.getId()
        current = get_workflow(self.context, workflow_tool.getChainFor(type_id))
        target = get_workflow(self.context, target_chain)
        errors = check_state_map(body.get("state_map"), target)
        if errors:
            self.raise_errors(errors)
        if body.get("dry_run"):
            return {
                "workflow": workflow_id(target),
                "current": workflow_id(current),
                **plan_change(self.context, [type_id], current, target),
            }
        changed = apply_change(
            self.context, [type_id], chain, current, target, body.get("state_map")
        )
        notify(ConfigurationChangedEvent(self, {"workflow": workflow_id(target)}))
        return {
            "workflow": workflow_id(target),
            "follows_default": chain == DEFAULT_CHAIN,
            "changed": changed,
        }
