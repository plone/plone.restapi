from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from plone.restapi.services.locking import lock_info
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Locking:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {"lock": {"@id": f"{self.context.absolute_url()}/@lock"}}
        if not expand:
            return result

        result["lock"].update(
            lock_info(self.context)
        )
        return result


class Lock(Service):
    """ Lock information about the current lock """

    def reply(self):
        locking = Locking(self.context, self.request)
        return locking(expand=True)["lock"]
