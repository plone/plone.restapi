from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import getUtility


class QuerystringGet(Service):
    """Returns the querystring configuration.

    This basically does the same thing as the '@@querybuilderjsonconfig'
    view from p.a.querystring, but exposes the config via the REST API.
    """

    def reply(self):
        registry = getUtility(IRegistry)
        reader = getMultiAdapter((registry, self.request), IQuerystringRegistryReader)

        result = reader()
        result["@id"] = "%s/@querystring" % self.context.absolute_url()
        return result
