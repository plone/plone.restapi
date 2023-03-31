from plone.restapi.services import Service
from plone.restapi.deserializer import json_body
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.admin import Upgrade
from zope.interface import alsoProvides

import plone


class UpgradeSitePost(Service):
    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        data = json_body(self.request)
        dry_run = data.get("dry_run", False)
        pm = getToolByName(self.context, "portal_migration")
        report = pm.upgrade(REQUEST=self.request, dry_run=dry_run)
        view = Upgrade(self.context, self.request)
        versions = view.versions()
        gs_fs = versions["fs"]
        gs_instance = versions["instance"]
        return {
            "@id": f"{self.context.absolute_url()}/@upgrade",
            "report": report,
            "versions": {
                "instance": gs_instance,
                "fs": gs_fs,
            },
            "dry_run": dry_run,
            "upgraded": gs_instance == gs_fs,
        }
