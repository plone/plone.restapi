from plone.app.multilingual.interfaces import ITranslatable
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName


class MissingTranslationsGet(Service):
    def reply(self):
        tool = getToolByName(self.context, "portal_languages", None)
        pcatalog = getToolByName(self.context, "portal_catalog", None)
        languages = tool.getSupportedLanguages()
        num_lang = len(languages)

        missing_translations = []
        already_added_canonicals = []

        brains = pcatalog.unrestrictedSearchResults(
            object_provides=ITranslatable.__identifier__
        )
        breakpoint()
        for brain in brains:
            tg = brain.TranslationGroup
            tg_members_brains = pcatalog.searchResults(TranslationGroup=tg)
            if len(tg_members_brains) < num_lang and tg not in already_added_canonicals:
                translated_languages = [a.Language for a in tg_members_brains]
                missing_languages = [
                    lang for lang in languages if lang not in translated_languages
                ]
                missing_translations.append(
                    {
                        "url": brain.getURL(),
                        "missing": missing_languages,
                        "@type": brain.portal_type,
                    }
                )

            already_added_canonicals.append(tg)

        return missing_translations
