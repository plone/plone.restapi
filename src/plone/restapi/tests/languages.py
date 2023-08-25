from plone.app.i18n.locales.languages import ContentLanguages
from plone.app.i18n.locales.languages import MetadataLanguages
from plone.i18n.locales.languages import _combinedlanguagelist
from plone.i18n.locales.languages import _languagelist


class ModifiableLanguages:
    """Mixin for the `IModifiableLanguageAvailability` based local utilities
    that makes the getLanguages and getLanguageListing methods
    (queried by portal_languages) also respect *modifiable* language
    availability.

    These methods would otherwise be inherited from LanguageAvailability
    (plone.i18n), and we override those here with variants that *do* respect
    modifiable language availability.

    This is so we can work with a limited set of languages in tests in order
    to avoid excessive language lists in response dumps included in docs.
    """

    def getLanguages(self, combined=False):
        """Return a sequence of Language objects for available languages."""
        languages = _languagelist.copy()
        if combined:
            languages.update(_combinedlanguagelist.copy())

        available = self.getAvailableLanguages(combined=combined)
        languages = {k: v for k, v in languages.items() if k in available}

        return languages

    def getLanguageListing(self, combined=False):
        """Return a sequence of language code and language name tuples."""
        languages = _languagelist.copy()
        if combined:
            languages.update(_combinedlanguagelist.copy())

        available = self.getAvailableLanguages(combined=combined)
        languages = {k: v for k, v in languages.items() if k in available}

        return [(code, languages[code]["name"]) for code in languages]


class ModifiableContentLanguages(ModifiableLanguages, ContentLanguages):
    """Overrides /plone/plone_app_content_languages with a variant that
    fully respects modifiable language availability.
    """


class ModifiableMetadataLanguages(ModifiableLanguages, MetadataLanguages):
    """Overrides /plone/plone_app_metadata_languages with a variant that
    fully respects modifiable language availability.
    """
