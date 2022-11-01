from plone.restapi.services import Service
from Products.CMFPlone.browser.admin import Upgrade


def format_steps(upgrades):
    steps = {}
    for group in upgrades:
        key = f"{group[0]['ssource']}-{group[0]['sdest']}"
        steps[key] = []
        for info in group:
            steps[key].append({"id": info["id"], "title": info["title"]})
    return steps


class UpgradeSiteGet(Service):
    def reply(self):
        view = Upgrade(self.context, self.request)
        versions = view.versions()
        upgrade_steps = format_steps(view.upgrades())
        return {
            "@id": f"{self.context.absolute_url()}/@upgrade",
            "upgrade_steps": upgrade_steps,
            "versions": {
                "instance": versions["instance"],
                "fs": versions["fs"],
            },
        }
