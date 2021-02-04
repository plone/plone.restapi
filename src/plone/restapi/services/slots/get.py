from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISlots
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class SlotsGet(Service):
    """Returns the available slots."""

    def __init__(self, context, request):
        super(SlotsGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        self.params.append(name)
        return self

    def reply(self):
        storage = ISlots(self.context)

        if self.params and len(self.params) > 0:
            return self.replySlot()

        storage = ISlots(self.context)

        adapter = getMultiAdapter(
            (self.context, storage, self.request), ISerializeToJson
        )

        return adapter()

    def replySlot(self):
        name = self.params[0]
        storage = ISlots(self.context)

        try:
            slot = storage[name]
            return getMultiAdapter(
                (self.context, slot, self.request), ISerializeToJson
            )(name)
        except KeyError:
            self.request.response.setStatus(404)
            return {
                "type": "NotFound",
                "message": 'Tile "{}" could not be found.'.format(self.params[0]),
            }
