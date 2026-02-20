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
        reader.vocab_context = self.context
        result = reader()

        # Convert dict indexes to ordered list to guarantee order in JSON
        if isinstance(result.get("indexes"), dict):
            result["indexes"] = [
                {"id": key, **value} for key, value in result["indexes"].items()
            ]

        # Convert sortable_indexes to ordered list
        if isinstance(result.get("sortable_indexes"), dict):
            result["sortable_indexes"] = [
                {"id": key, **value}
                for key, value in result["sortable_indexes"].items()
            ]

        result["@id"] = f"{self.context.absolute_url()}/@querystring"
        return result
