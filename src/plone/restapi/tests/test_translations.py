from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING
from Products.CMFPlone.interfaces import ILanguage

from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import requests
import transaction
import unittest


class TestTranslationInfo(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title="Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        ITranslationManager(self.en_content).register_translation("es", self.es_content)

    def test_translation_info_includes_translations(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request), name="GET_application_json_@translations"
        )

        info = tinfo.reply()
        self.assertIn("items", info)
        self.assertEqual(1, len(info["items"]))

    def test_correct_translation_information(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request), name="GET_application_json_@translations"
        )

        info = tinfo.reply()
        tinfo_es = info["items"][0]
        self.assertEqual(self.es_content.absolute_url(), tinfo_es["@id"])
        self.assertEqual(
            ILanguage(self.es_content).get_language(), tinfo_es["language"]
        )

    def test_translation_info_includes_root_translations(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request), name="GET_application_json_@translations"
        )

        info = tinfo.reply()
        self.assertIn("root", info)
        self.assertEqual(4, len(info["root"]))


class TestLinkContentsAsTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title="Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        transaction.commit()

    def test_translation_linking_by_url(self):
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        for language, translation in manager.get_translations():
            if language == ILanguage(self.es_content).get_language():
                self.assertEqual(translation, self.es_content)

    def test_translation_linking_by_path(self):
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": "/es/test-document"},
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        for language, translation in manager.get_translations():
            if language == ILanguage(self.es_content).get_language():
                self.assertEqual(translation, self.es_content)

    def test_translation_linking_by_uid(self):
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.UID()},
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        for language, translation in manager.get_translations():
            if language == ILanguage(self.es_content).get_language():
                self.assertEqual(translation, self.es_content)

    def test_calling_endpoint_without_id_gives_400(self):
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_already_translated_content_gives_400(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_inexistent_content_gives_400(self):
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": "http://this-content-does-not-exist"},
        )
        self.assertEqual(400, response.status_code)

    def test_get_translations_on_content_with_no_permissions(self):
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(201, response.status_code)
        api.content.transition(self.en_content, "publish")
        transaction.commit()

        response = requests.get(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertTrue(len(response["items"]) == 0)

    def test_link_translation_with_an_already_translated_content_returns_400(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json()["error"]["message"],
            "Source already translated into language es",
        )

    def test_link_translation_with_target_already_linked_to_other_object_returns_400(
        self,
    ):
        self.en_content_2 = createContentInContainer(
            self.portal["en"], "Document", title="Test document 2"
        )
        ITranslationManager(self.en_content_2).register_translation(
            "es", self.es_content
        )
        transaction.commit()
        response = requests.post(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json()["error"]["message"],
            "Target already translated into language es",
        )

    def test_link_translation_with_LFRs_not_possible_since_they_are_protected_returns_400(
        self,
    ):
        response = requests.post(
            f"{self.es_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.portal["en"].absolute_url()},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json()["error"]["message"],
            "Language Root Folders can only be linked between each other",
        )


class TestUnLinkContentTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title="Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()

    def test_translation_unlinking_succeeds(self):
        response = requests.delete(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"language": "es"},
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        self.assertNotIn(
            ILanguage(self.es_content).get_language(), list(manager.get_translations())
        )

    def test_calling_endpoint_without_language_gives_400(self):
        response = requests.delete(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_untranslated_content_gives_400(self):
        ITranslationManager(self.en_content).remove_translation("es")
        transaction.commit()
        response = requests.delete(
            f"{self.en_content.absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"language": "es"},
        )
        self.assertEqual(400, response.status_code)

    def test_translation_unlinking_a_LRF_errors(self):
        response = requests.delete(
            f"{self.portal['en'].absolute_url()}/@translations",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"language": "es"},
        )
        self.assertEqual(400, response.status_code)
        self.assertEqual(
            response.json()["error"]["message"],
            "Language Root Folders cannot be unlinked",
        )


class TestCreateContentsAsTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        transaction.commit()

    def test_post_to_folder_creates_document_translated(self):
        response = requests.post(
            f"{self.portal.absolute_url()}/de",
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "@type": "Document",
                "id": "mydocument",
                "title": "My Document DE",
                "translation_of": self.es_content.UID(),
                "language": "de",
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.commit()

        manager = ITranslationManager(self.es_content)

        self.assertTrue("de" in manager.get_translations())
        self.assertEqual("My Document DE", manager.get_translations()["de"].title)

        self.assertEqual("Document", response.json().get("@type"))
        self.assertEqual("mydocument", response.json().get("id"))
        self.assertEqual("My Document DE", response.json().get("title"))


class TestTranslationLocator(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        transaction.commit()

    def test_translation_locator(self):
        response = requests.get(
            "{}/@translation-locator?target_language=de".format(
                self.es_content.absolute_url()
            ),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertEqual(200, response.status_code)

        self.assertEqual(self.portal_url + "/de", response.json().get("@id"))
