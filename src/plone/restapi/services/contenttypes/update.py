from plone.restapi.services.contenttypes import ContentTypesService


class ContentTypesPatch(ContentTypesService):
    def reply(self):
        fti = self.get_fti()
        self.update(fti, self.json_body())
        return self.reply_no_content()
