from AccessControl.SecurityManagement import getSecurityManager
from plone.rest import Service as RestService
from plone.restapi.permissions import UseRESTAPI
from plone.restapi.problem_types import get_backwards_compat
from plone.restapi.problem_types import INTERNAL_ERROR
from plone.restapi.problem_types import STATUS_MAP
from plone.restapi.problem_types import translate_message
from zExceptions import Unauthorized

import json

_no_content_marker = object()


class Service(RestService):
    """Base class for Plone REST API services"""

    content_type = "application/json"

    def render(self):
        self.check_permission()
        content = self.reply()
        if content is not _no_content_marker:
            if (
                not get_backwards_compat()
                and isinstance(content, dict)
                and "error" in content
            ):
                content = self._convert_error_to_rfc7807(content)
            self.request.response.setHeader("Content-Type", self.content_type)
            return json.dumps(
                content, indent=2, sort_keys=True, separators=(", ", ": ")
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

    def _convert_error_to_rfc7807(self, error_dict):
        """Convert legacy error format to RFC 7807 Problem Details.

        Takes a dict with an 'error' key and converts it to RFC 7807 format.
        Backwards compatible fields are included based on the backwards compat flag.
        Preserves special fields like 'errors' for form validation errors.
        """
        error = error_dict.get("error", {})
        status = self.request.response.getStatus()
        problem_type, title = STATUS_MAP.get(
            status, (INTERNAL_ERROR, "Internal Server Error")
        )

        message = error.get("message", "")
        translated_message = translate_message(message, self.request)

        error_response = {
            "type": problem_type,
            "title": title,
            "status": status,
            "detail": translated_message,
            "instance": self.request.get("PATH_INFO", ""),
        }

        if get_backwards_compat():
            error_response["message"] = translated_message
            error_response["error_type"] = error.get("type", "")
            if "errors" in error:
                error_response["errors"] = error["errors"]

        return error_response
