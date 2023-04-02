from plone.restapi.services import Service


try:
    from Products.CMFPlone.controlpanel.browser.overview import OverviewControlPanel
except ImportError:
    from plone.app.controlpanel.overview import OverviewControlPanel

import pkg_resources


plone_restapi_version = pkg_resources.require("plone.restapi")[0].version


class SystemGet(Service):
    def reply(self):
        overview_control_panel = OverviewControlPanel(self.context, self.request)
        core_versions = overview_control_panel.core_versions()
        gs_fs = core_versions.get("Plone File System")
        gs_instance = core_versions.get("Plone Instance")
        return {
            "@id": f"{self.context.absolute_url()}/@system",
            "zope_version": core_versions.get("Zope"),
            "plone_version": core_versions.get("Plone"),
            "plone_restapi_version": plone_restapi_version,
            "python_version": core_versions.get("Python"),
            "cmf_version": core_versions.get("CMF"),
            "pil_version": core_versions.get("PIL"),
            "debug_mode": core_versions.get("Debug mode"),
            "plone_gs_metadata_version_installed": gs_instance,
            "plone_gs_metadata_version_file_system": gs_fs,
            "upgrade": gs_fs != gs_instance,
        }
