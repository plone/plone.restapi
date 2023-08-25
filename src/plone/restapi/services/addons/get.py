from plone.restapi.services import Service
from plone.restapi.services.addons.addons import Addons
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class AddonsGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        self.addons = Addons(context, request)
        self.query = self.request.form.copy()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@addons as parameters
        self.params.append(name)
        return self

    def reply(self):
        all_addons = self.addons.get_addons()

        if self.params:
            if self.params[0] in all_addons:
                return self.addons.serializeAddon(all_addons[self.params[0]])
            else:
                return []

        result = {
            "items": {"@id": f"{self.context.absolute_url()}/@addons"},
        }
        addons_data = []
        for addon in all_addons.values():
            addons_data.append(self.addons.serializeAddon(addon))

        if len(self.query) > 0 and len(self.params) == 0:
            upgradeables = self.query.get("upgradeable", "")
            if upgradeables:
                addons_data = [
                    addon
                    for addon in addons_data
                    if addon.get("upgrade_info", False)
                    and addon["upgrade_info"].get("available", False)
                ]

        result["items"] = addons_data
        self.request.response.setStatus(200)
        return result
