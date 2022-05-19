from plone.restapi.services import Service


class RelationsPost(Service):
    """Creates new relations relevant to the context"""

    def reply(self):
        raise NotImplementedError()


class RelationsCatalogPost(Service):
    """Creates all kinds of relations."""

    def reply(self):
        raise NotImplementedError()
