# -*- coding: utf-8 -*-
from plone.restapi.services import Service

try:
    from Products.CMFPlone.controlpanel.browser.overview import OverviewControlPanel
except ImportError:
    from plone.app.controlpanel.overview import OverviewControlPanel


class SystemGet(Service):
    def reply(self):
        overview_control_panel = OverviewControlPanel(self.context, self.request)
        core_versions = overview_control_panel.core_versions()
        return {
            "@id": "{}/@system".format(self.context.absolute_url()),
            "zope_version": core_versions.get("Zope"),
            "plone_version": core_versions.get("Plone"),
            "python_version": core_versions.get("Python"),
            "cmf_version": core_versions.get("CMF"),
            "pil_version": core_versions.get("PIL"),
            "debug-mode": core_versions.get("Debug mode"),
            "plone_gs_metadata_version_installed": core_versions.get("Plone Instance"),
            "plone_gs_metadata_version_file_system": core_versions.get(
                "Plone File System"
            ),
        }
