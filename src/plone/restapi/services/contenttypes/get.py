from plone.restapi.services.contenttypes import ContentTypesService
from plone.restapi.services.contenttypes import WORKFLOW
from plone.restapi.typesettings.manage import count_items
from Products.CMFCore.utils import getToolByName


class ContentTypesGet(ContentTypesService):
    def reply(self):
        if self.params[1:] == [WORKFLOW]:
            type_id = self.get_fti(WORKFLOW).getId()
            return {
                "@id": f"{self.url(type_id)}/{WORKFLOW}",
                **self.workflow(type_id),
            }
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
