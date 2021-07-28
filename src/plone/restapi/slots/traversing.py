from plone.rest.traverse import RESTWrapper
from plone.restapi.slots.interfaces import ISlots
from zExceptions import NotFound
from zope.traversing.namespace import SimpleHandler


class RestSlotsTraversing(SimpleHandler):
    ''' rest attachment traversing '''

    name = None

    def __init__(self, context, request=None):
        self.context = context

    def traverse(self, name, remaining):
        ''' traverse '''

        slots = ISlots(self.context.context)

        if name not in slots:
            raise NotFound

        # self.context is a RESTWrapper
        storage = slots.__of__(self.context.context)

        return RESTWrapper(storage[name], self.context.request)
