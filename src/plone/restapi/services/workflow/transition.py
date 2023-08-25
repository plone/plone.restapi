from DateTime import DateTime
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from plone.restapi.services.workflow.utils import elevated_privileges
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.i18n import translate
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.publisher.interfaces import NotFound

import plone.protect.interfaces


@implementer(IPublishTraverse)
class WorkflowTransition(Service):
    """Trigger workflow transition"""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.transition = None
        self.wftool = getToolByName(context, "portal_workflow")

    def publishTraverse(self, request, name):
        if self.transition is None:
            self.transition = name
        else:
            raise NotFound(self, name, request)
        return self

    def reply(self):
        if self.transition is None:
            self.request.response.setStatus(400)
            return dict(error=dict(type="BadRequest", message="Missing transition"))

        data = json_body(self.request)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        comment = data.get("comment", "")
        include_children = data.get("include_children", False)
        publication_dates = {}
        if "effective" in data:
            publication_dates["effective"] = data["effective"]
        if "expires" in data:
            publication_dates["expires"] = data["expires"]
        # Archetypes has different field names
        if "effectiveDate" in data:
            publication_dates["effectiveDate"] = data["effectiveDate"]
        if "expirationDate" in data:
            publication_dates["expirationDate"] = data["expirationDate"]

        try:
            self.recurse_transition(
                [self.context], comment, publication_dates, include_children
            )

        except WorkflowException as e:
            self.request.response.setStatus(400)
            return dict(
                error=dict(
                    type="WorkflowException",
                    message=translate(str(e), context=self.request),
                )
            )
        except BadRequest as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="Bad Request", message=str(e)))

        with elevated_privileges(self.context):
            try:
                history = self.wftool.getInfoFor(self.context, "review_history")
                action = history[-1]
                action["title"] = self.context.translate(
                    self.wftool.getTitleForStateOnType(
                        action["review_state"], self.context.portal_type
                    )
                )
            except WorkflowException as e:
                self.request.response.setStatus(400)
                action = dict(
                    error=dict(
                        type="WorkflowException",
                        message=translate(str(e), context=self.request),
                    )
                )

        return json_compatible(action)

    def recurse_transition(
        self, objs, comment, publication_dates, include_children=False
    ):
        for obj in objs:
            if publication_dates:
                deserializer = queryMultiAdapter(
                    (obj, self.request), IDeserializeFromJson
                )
                deserializer(data=publication_dates)

            if obj.EffectiveDate() == "None":
                obj.setEffectiveDate(DateTime())
                obj.reindexObject()
            if not self.wftool.getWorkflowsFor(obj):
                continue
            try:
                self.wftool.doActionFor(obj, self.transition, comment=comment)
            except WorkflowException as e:
                if not self.is_same_state(obj):
                    # this is a real error
                    raise e
            if include_children and IFolderish.providedBy(obj):
                self.recurse_transition(
                    obj.objectValues(), comment, publication_dates, include_children
                )

    def is_same_state(self, obj):
        """
        Return True if the object is already in the transition's destination state.
        """
        review_state = self.wftool.getInfoFor(ob=obj, name="review_state")

        for wf in self.wftool.getWorkflowsFor(obj):
            for transition in wf.transitions.objectValues():
                if (
                    review_state == transition.new_state_id
                    and self.transition == transition.id
                ):
                    return True
        return False
