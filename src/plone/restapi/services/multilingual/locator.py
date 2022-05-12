from plone.restapi.services import Service
from plone.app.multilingual.interfaces import ITranslationLocator


class TranslationLocator(Service):
    """Get translation locator placements information"""

    def reply(self):
        target_language = self.request.form["target_language"]

        locator = ITranslationLocator(self.context)
        parent = locator(target_language)

        return {"@id": parent.absolute_url()}
