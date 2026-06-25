from plone.restapi.interfaces import IRenderer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import _no_content_marker
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter


class ContentGet(Service):
    """Returns a serialized content object."""

    def render(self):
        self.check_permission()
        content = self.reply()
        if content is _no_content_marker:
            return
        mime_type = self.request.getHeader("Accept").split(";")[0].strip()
        if mime_type == "*/*":
            mime_type = "application/json"
        renderer = getMultiAdapter(
            (self.context, self.request), IRenderer, name=mime_type
        )
        self.request.response.setHeader("Content-Type", renderer.content_type)
        self.request.response.setHeader("Vary", "Accept")
        return renderer(content)

    def reply(self):
        serializer = queryMultiAdapter((self.context, self.request), ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message="No serializer available."))

        return serializer(version=self.request.get("version"))
