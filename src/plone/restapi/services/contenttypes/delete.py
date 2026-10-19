from plone.dexterity.interfaces import IDexterityFTI
from plone.restapi.services.contenttypes import ContentTypesService
from plone.restapi.typesettings.manage import count_items
from plone.restapi.typesettings.manage import remove_type
from zExceptions import BadRequest


class ContentTypesDelete(ContentTypesService):
    def reply(self):
        fti = self.get_fti()
        type_id = fti.getId()
        if type_id == "Plone Site":
            raise BadRequest("The site content type cannot be deleted")
        if not IDexterityFTI.providedBy(fti):
            raise BadRequest("Only Dexterity content types can be deleted")
        items_total = count_items(self.context).get(type_id, 0)
        if items_total:
            self.request.response.setStatus(409)
            return {
                "error": {
                    "type": "Conflict",
                    "message": "The content type still has items",
                },
                "items_total": items_total,
            }
        remove_type(self.types_tool, type_id, self.request)
        return self.reply_no_content()
