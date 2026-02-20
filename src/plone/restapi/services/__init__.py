from AccessControl.SecurityManagement import getSecurityManager
from plone.rest import Service as RestService
from plone.restapi.permissions import UseRESTAPI
from zExceptions import Unauthorized

import json


_no_content_marker = object()


class Service(RestService):
    content_type = "application/json"

    def render(self):
        self.check_permission()
        content = self.reply()
        if content is not _no_content_marker:
            self.request.response.setHeader("Content-Type", self.content_type)
            sort_keys = getattr(self, "sort_keys", True)
            return json.dumps(
                content, indent=2, sort_keys=sort_keys, separators=(", ", ": ")
            )

    def check_permission(self):
        sm = getSecurityManager()
        if not sm.checkPermission(UseRESTAPI, self):
            raise Unauthorized("Missing %r permission" % UseRESTAPI)

    def reply(self):
        return _no_content_marker

    def reply_no_content(self, status=204):
        self.request.response.setStatus(status)
        return _no_content_marker
