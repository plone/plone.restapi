from AccessControl.SecurityManagement import getSecurityManager
from plone.rest import Service as RestService
from plone.restapi.interfaces import IRenderer
from plone.restapi.permissions import UseRESTAPI
from zExceptions import Unauthorized
from zope.component import queryAdapter

import json

_no_content_marker = object()


class Service(RestService):
    """Base class for Plone REST API services"""

    content_type = "application/json"

    def render(self):
        self.check_permission()
        content = self.reply()
        if content is not _no_content_marker:
            # Content negotiation: select renderer based on Accept header
            renderer, content_type = self._get_renderer()
            # Allow services to explicitly override the content type.
            # If the service has set an instance attribute content_type in reply(),
            # use that instead of the negotiated content type.
            # If the service class defines content_type (not inherited from Service),
            # also respect that for backwards compatibility.
            if "content_type" in self.__dict__ or (
                "content_type" in self.__class__.__dict__ and self.content_type
            ):
                content_type = self.content_type
            self.request.response.setHeader("Content-Type", content_type)
            return renderer(content)

    def _get_renderer(self):
        """Select the appropriate renderer based on Accept header.

        Returns a tuple of (renderer_callable, content_type).
        """
        # Get Accept header
        accept_header = self.request.getHeader("Accept", "")

        # Parse Accept header and find the best match
        # Simple implementation - just check for the most common types
        # A full implementation would parse quality values (q=0.8, etc.)
        accepted_types = [
            mime_type.strip().split(";")[0]
            for mime_type in accept_header.split(",")
            if mime_type.strip()
        ]

        # Try to find a renderer for each accepted type
        for mime_type in accepted_types:
            if mime_type == "*/*":
                # Wildcard - use default JSON
                continue

            renderer = queryAdapter(self.request, IRenderer, name=mime_type)
            if renderer is not None:
                return renderer, renderer.content_type

        # Fallback to JSON (default)
        renderer = queryAdapter(self.request, IRenderer, name="application/json")
        if renderer is not None:
            return renderer, renderer.content_type

        # Ultimate fallback - inline JSON rendering
        return (
            lambda data: json.dumps(
                data, indent=2, sort_keys=True, separators=(", ", ": ")
            ),
            "application/json",
        )

    def check_permission(self):
        sm = getSecurityManager()
        if not sm.checkPermission(UseRESTAPI, self):
            raise Unauthorized("Missing %r permission" % UseRESTAPI)

    def reply(self):
        """Process the request and return a JSON serializable data structure or
        the no content marker if the response body should be empty.
        """
        return _no_content_marker

    def reply_no_content(self, status=204):
        self.request.response.setStatus(status)
        return _no_content_marker
