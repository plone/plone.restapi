from . import Slot
from .interfaces import ISlotStorage
from plone.rest.traverse import RESTWrapper
from plone.restapi.slots.interfaces import ISlots
from zExceptions import NotFound
from zope.traversing.namespace import SimpleHandler


def get_slot(context, name):
    slots = ISlots(context)

    if name not in slots:
        raise NotFound

    storage = ISlotStorage(context)
    slot = storage.get(name, None)
    if not slot:
        slot = Slot()

    slot = slot.__of__(context)

    return slot


class SlotsTraversing(SimpleHandler):
    ''' REST attachment traversing '''

    name = None

    def __init__(self, context, request=None):
        self.context = context
        self.request = request

    def traverse(self, name, remaining):
        ''' traverse '''

        slot = get_slot(self.context, name)
        wrapper = RESTWrapper(slot, self.request)
        return wrapper


class RestSlotsTraversing(SimpleHandler):
    ''' REST slots traversing '''

    name = None

    def __init__(self, context, request=None):
        self.context = context

    def traverse(self, name, remaining):
        ''' traverse '''

        # self.context is a RESTWrapper
        slot = get_slot(self.context.context)

        return RESTWrapper(slot, self.context.request)
