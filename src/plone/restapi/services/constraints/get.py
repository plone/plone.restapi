from plone.restapi.services import Service
from plone.restapi.services.constraints import serialize_constraints


class ConstraintsGet(Service):
    """Return addable-type constraint settings for the current context."""

    def reply(self):
        return serialize_constraints(self.context)
