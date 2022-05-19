from plone.restapi.services import Service


class RelationsDelete(Service):
    """Deletes relations relevant to the context."""

    def reply(self):
        raise NotImplementedError()


class RelationsCatalogDelete(Service):
    """Delete all kinds of relations."""

    def reply(self):
        raise NotImplementedError()
