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
        result["items"] = addons_data
        self.request.response.setStatus(200)
        return result
