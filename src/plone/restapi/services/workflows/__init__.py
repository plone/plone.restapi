from plone.protect.interfaces import IDisableCSRFProtection
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.services import Service
from plone.restapi.types.utils import _format_errors
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

SERVICE_ID = "@workflows"


@implementer(IPublishTraverse)
class WorkflowsService(Service):
    """Base class for @workflows services."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        if request.method != "GET":
            alsoProvides(request, IDisableCSRFProtection)

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    @property
    def workflow_tool(self):
        return getToolByName(self.context, "portal_workflow")

    def url(self, workflow_id=None):
        url = f"{self.context.absolute_url()}/{SERVICE_ID}"
        return url if workflow_id is None else f"{url}/{workflow_id}"

    def json_body(self):
        try:
            body = json_body(self.request)
        except DeserializationError as exc:
            self.raise_errors([{"message": str(exc), "error": exc}])
        if not isinstance(body, dict):
            self.raise_errors([{"message": "Expected an object", "error": None}])
        return body

    def raise_errors(self, errors):
        raise BadRequest(_format_errors(errors, self.request))
