from plone.dexterity.interfaces import IDexterityContent
from plone.i18n.interfaces import ILanguageSchema
from plone.restapi import HAS_MULTILINGUAL
from plone.restapi.deserializer.dxfields import ChoiceFieldDeserializer
from plone.restapi.interfaces import IControlpanelLayer
from plone.restapi.interfaces import IFieldDeserializer
from zope.component import adapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.schema.interfaces import IChoice

if HAS_MULTILINGUAL:
    from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled


@implementer(IFieldDeserializer)
@adapter(IChoice, IDexterityContent, IControlpanelLayer)
class ControlpanelLanguageFieldDeserializer(ChoiceFieldDeserializer):
    def __call__(self, value):
        value = super().__call__(value)

        if (
            self.field.interface is ILanguageSchema
            and self.field.getName() == "default_language"
        ):
            self._sync_site_language(value)

        return value

    def _sync_site_language(self, language):
        if not IControlpanelLayer.providedBy(self.request):
            return

        if HAS_MULTILINGUAL and IPloneAppMultilingualInstalled.providedBy(self.request):
            return

        portal = getSite()
        if portal is None:
            return

        if portal.Language() == language:
            return

        portal.setLanguage(language)
        self.request["HTTP_ACCEPT_LANGUAGE"] = language
