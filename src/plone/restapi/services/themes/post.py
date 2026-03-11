import zipfile

from plone.app.theming.interfaces import IThemeSettings
from plone.app.theming.plugins.utils import getPlugins
from plone.app.theming.utils import applyTheme
from plone.app.theming.utils import extractThemeInfo
from plone.app.theming.utils import getOrCreatePersistentResourceDirectory
from plone.protect.interfaces import IDisableCSRFProtection
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import alsoProvides


class ThemesPost(Service):
    def reply(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        theme_archive = self.request.form.get("themeArchive")
        if not theme_archive:
            self.request.response.setStatus(400)
            return {"error": "Missing 'themeArchive' field"}

        enable = self.request.form.get("enable", "false").lower() == "true"
        replace = self.request.form.get("replace", "false").lower() == "true"

        try:
            theme_zip = zipfile.ZipFile(theme_archive)
        except (zipfile.BadZipFile, zipfile.LargeZipFile) as e:
            self.request.response.setStatus(400)
            return {"error": f"Invalid zip file: {e}"}

        try:
            theme_info = extractThemeInfo(theme_zip, checkRules=False)
        except (ValueError, KeyError) as e:
            self.request.response.setStatus(400)
            return {"error": f"Invalid theme: {e}"}

        theme_container = getOrCreatePersistentResourceDirectory()
        theme_name = theme_info.__name__

        if theme_name in theme_container:
            if not replace:
                self.request.response.setStatus(409)
                return {
                    "error": f"Theme '{theme_name}' already exists. Use replace=true to overwrite."
                }
            del theme_container[theme_name]

        theme_container.importZip(theme_zip)

        # Call plugin lifecycle hooks
        theme_directory = theme_container[theme_name]
        for _name, plugin in getPlugins():
            plugin.onCreated(theme_name, {}, theme_directory)

        if enable:
            applyTheme(theme_info)
            registry = getUtility(IRegistry)
            settings = registry.forInterface(IThemeSettings, False)
            settings.enabled = True

        self.request.response.setStatus(201)
        return {
            "@id": f"{self.context.absolute_url()}/@themes/{theme_name}",
            "id": theme_name,
            "title": theme_info.title,
        }
