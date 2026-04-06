"""JSON Renderer - converts Python data structures to JSON."""

from plone.restapi.interfaces import IRenderer
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface

import json


@implementer(IRenderer)
@adapter(Interface)
class JSONRenderer:
    """Render data as JSON."""

    content_type = "application/json"

    def __init__(self, request):
        self.request = request

    def __call__(self, data):
        """Convert Python data structure to formatted JSON string."""
        return json.dumps(data, indent=2, sort_keys=True, separators=(", ", ": "))
