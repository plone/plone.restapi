from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.i18n.interfaces import ILanguageSchema
from plone.registry.interfaces import IRegistry
from plone.restapi import HAS_MULTILINGUAL
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import transaction
import unittest

if HAS_MULTILINGUAL:
    from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled


class TestLanguageControlpanel(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_update_language_syncs_site_language(self):
        registry = getUtility(IRegistry)
        language_settings = registry.forInterface(
            ILanguageSchema, prefix="plone", check=False
        )
        old_default_language = language_settings.default_language
        old_site_language = self.portal.Language()
        new_language = "de"

        try:
            self.portal.setLanguage("en")
            language_settings.default_language = "en"
            transaction.commit()

            response = self.api_session.patch(
                "/@controlpanels/language",
                json={"default_language": new_language},
            )
            transaction.begin()

            self.assertEqual(204, response.status_code)
            self.assertEqual(new_language, language_settings.default_language)
            self.assertEqual(new_language, self.portal.Language())
        finally:
            language_settings.default_language = old_default_language
            self.portal.setLanguage(old_site_language)
            transaction.commit()

    def test_update_non_language_choice_field_does_not_sync_site_language(self):
        old_site_language = self.portal.Language()

        try:
            self.portal.setLanguage("en")
            transaction.commit()
            response = self.api_session.patch(
                "/@controlpanels/editing",
                json={"default_editor": "TinyMCE"},
            )
            transaction.begin()

            self.assertEqual(204, response.status_code)
            self.assertEqual("en", self.portal.Language())
        finally:
            self.portal.setLanguage(old_site_language)
            transaction.commit()

    def test_update_invalid_language_does_not_sync_site_language(self):
        old_site_language = self.portal.Language()

        try:
            self.portal.setLanguage("en")
            transaction.commit()
            response = self.api_session.patch(
                "/@controlpanels/language",
                json={"default_language": "not-a-language"},
            )
            transaction.begin()

            self.assertEqual(400, response.status_code)
            self.assertEqual("en", self.portal.Language())
        finally:
            self.portal.setLanguage(old_site_language)
            transaction.commit()


@unittest.skipUnless(HAS_MULTILINGUAL, "plone.app.multilingual is not installed")
class TestMultilingualLanguageControlpanel(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_update_language_does_not_sync_site_language_on_multilingual_site(self):
        if not IPloneAppMultilingualInstalled.providedBy(self.request):
            self.skipTest("plone.app.multilingual is not enabled")

        registry = getUtility(IRegistry)
        language_settings = registry.forInterface(
            ILanguageSchema, prefix="plone", check=False
        )
        old_default_language = language_settings.default_language
        old_site_language = self.portal.Language()
        new_language = "de"

        try:
            self.portal.setLanguage("en")
            language_settings.default_language = "en"
            transaction.commit()

            response = self.api_session.patch(
                "/@controlpanels/language",
                json={"default_language": new_language},
            )
            transaction.begin()

            self.assertEqual(204, response.status_code)
            self.assertEqual(new_language, language_settings.default_language)
            self.assertEqual("en", self.portal.Language())
        finally:
            language_settings.default_language = old_default_language
            self.portal.setLanguage(old_site_language)
            transaction.commit()
