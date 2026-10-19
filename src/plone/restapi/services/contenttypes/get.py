from plone.restapi.services.contenttypes import ContentTypesService
from plone.restapi.typesettings.manage import count_items
from Products.CMFCore.utils import getToolByName


class ContentTypesGet(ContentTypesService):
    def reply(self):
        if self.params:
            return self.serialize(self.get_fti())
        counts = count_items(self.context)
        workflow = getToolByName(self.context, "portal_workflow")
        chains = dict(workflow.listChainOverrides())
        items = [
            self.serialize(fti, counts=counts, chains=chains)
            for fti in self.types_tool.listTypeInfo()
        ]
        return {"@id": self.url(), "items": items, "items_total": len(items)}
