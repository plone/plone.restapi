# -*- coding: utf-8 -*-
from plone.rest import Service as RestService

import json

_no_content_marker = object()


class Service(RestService):
    """Base class for Plone REST API services
    """
    content_type = 'application/json'

    def render(self):
        content = self.reply()
        if content is not _no_content_marker:
            self.request.response.setHeader("Content-Type", self.content_type)
            return json.dumps(content, indent=2, sort_keys=True)

    def reply(self):
        """Process the request and return a JSON serializable data structure or
           the no content marker if the response body should be empty.
        """
        return _no_content_marker
