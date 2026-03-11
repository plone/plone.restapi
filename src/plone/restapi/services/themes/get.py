from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import getAvailableThemes
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ThemesGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IThemeSettings, False)
        current = settings.currentTheme

        themes = getAvailableThemes()

        if self.params:
            name = self.params[0]
            for theme in themes:
                if theme.__name__ == name:
                    return self._serialize(theme, current)
            self.request.response.setStatus(404)
            return {"error": "Theme not found"}

        return [self._serialize(t, current) for t in themes]

    def _serialize(self, theme, current_name):
        return {
            "@id": f"{self.context.absolute_url()}/@themes/{theme.__name__}",
            "id": theme.__name__,
            "title": theme.title,
            "description": theme.description,
            "active": theme.__name__ == current_name,
            "preview": theme.preview,
            "rules": theme.rules,
        }
