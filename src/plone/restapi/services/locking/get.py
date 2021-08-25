from plone.restapi.services import Service
from plone.restapi.services.locking import lock_info


class Lock(Service):
    """Lock information about the current lock"""

    def reply(self):
        return lock_info(self.context)
