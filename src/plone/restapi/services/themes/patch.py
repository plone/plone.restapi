from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.utils import applyTheme
from plone.app.theming.utils import getAvailableThemes
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class ThemesPatch(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)
        if not self.params:
            self.request.response.setStatus(400)
            return {"error": "Theme name required in URL"}

        theme_name = self.params[0]
        body = json_body(self.request)
        active = body.get("active")

        registry = getUtility(IRegistry)
        settings = registry.forInterface(IThemeSettings, False)

        if active is True:
            themes = getAvailableThemes()
            theme = next((t for t in themes if t.__name__ == theme_name), None)
            if theme is None:
                self.request.response.setStatus(404)
                return {"error": "Theme not found"}
            applyTheme(theme)
            settings.enabled = True
        elif active is False:
            applyTheme(None)
            settings.enabled = False
        else:
            self.request.response.setStatus(400)
            return {"error": "Body must contain 'active': true or false"}

        return self.reply_no_content()
