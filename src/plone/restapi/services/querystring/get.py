from plone.app.querystring.interfaces import IQuerystringRegistryReader
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getMultiAdapter
from zope.component import getUtility
from plone.restapi.services.vocabularies.get import VocabulariesGet

class QuerystringGet(Service):
    """Returns the querystring configuration, filtering based on user permissions."""
    
    def reply(self):
        registry = getUtility(IRegistry)
        reader = getMultiAdapter((registry, self.request), IQuerystringRegistryReader)
        reader.vocab_context = self.context
        result = reader()
        
        # Filter vocabularies based on user permissions
        vocabularies_get_service = VocabulariesGet(self.context, self.request)
        indexes_to_remove = []
        
        for index_name, index_data in result['indexes'].items():
            if 'vocabulary' in index_data:
                vocabulary_name = index_data['vocabulary']
                if not vocabularies_get_service._has_permission_to_access_vocabulary(vocabulary_name):
                    indexes_to_remove.append(index_name)
                    
        for index_name in indexes_to_remove:
            del result['indexes'][index_name]
        
        result["@id"] = f"{self.context.absolute_url()}/@querystring"
        return result
