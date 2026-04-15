from plone.restapi.interfaces import IRenderer
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import _no_content_marker
from plone.restapi.services import Service
from zope.component import queryAdapter
from zope.component import queryMultiAdapter


class ContentGet(Service):
    """Returns a serialized content object."""

    def render(self):
        self.check_permission()
        content = self.reply()
        if content is _no_content_marker:
            return
        accept = self.request.getHeader("Accept", "")
        for mime_type in [m.strip().split(";")[0] for m in accept.split(",")]:
            if mime_type and mime_type != "*/*":
                renderer = queryAdapter(self.request, IRenderer, name=mime_type)
                if renderer is not None:
                    self.request.response.setHeader(
                        "Content-Type", renderer.content_type
                    )
                    return renderer(content)
        renderer = queryAdapter(self.request, IRenderer, name="application/json")
        self.request.response.setHeader("Content-Type", renderer.content_type)
        return renderer(content)

    def reply(self):
        serializer = queryMultiAdapter((self.context, self.request), ISerializeToJson)

        if serializer is None:
            self.request.response.setStatus(501)
            return dict(error=dict(message="No serializer available."))

        return serializer(version=self.request.get("version"))
