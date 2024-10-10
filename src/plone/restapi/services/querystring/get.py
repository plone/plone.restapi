from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import getUtility

class QuerystringEditorGet(Service):
    """Returns the complete querystring configuration for editors.
    This maintains all existing functionality but requires edit permissions.
    """
    def reply(self):
        registry = getUtility(IRegistry)
        reader = getMultiAdapter((registry, self.request), IQuerystringRegistryReader)
        reader.vocab_context = self.context
        result = reader()
        result["@id"] = f"{self.context.absolute_url()}/@querystring"
        return result

class QuerystringPublicGet(Service):
    """Returns a filtered querystring configuration for public use.
    This removes sensitive information like user and group vocabularies.
    """
    def reply(self):
        registry = getUtility(IRegistry)
        reader = getMultiAdapter((registry, self.request), IQuerystringRegistryReader)
        reader.vocab_context = self.context
        result = reader()
        
        # Filter out sensitive information
        sensitive_vocabs = ['plone.app.vocabularies.Users', 'plone.app.vocabularies.Groups']
        indexes_to_remove = []
        
        for index_name, index_data in result['indexes'].items():
            if 'vocabulary' in index_data and index_data['vocabulary'] in sensitive_vocabs:
                indexes_to_remove.append(index_name)
                
        for index_name in indexes_to_remove:
            del result['indexes'][index_name]
        
        result["@id"] = f"{self.context.absolute_url()}/@querystring-public"
        return result
