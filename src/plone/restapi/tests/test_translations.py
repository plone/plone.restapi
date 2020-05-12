# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PAM_INSTALLED
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING
from zope.component import getMultiAdapter
from zope.interface import alsoProvides

import requests
import transaction
import unittest


if PAM_INSTALLED:
    from Products.CMFPlone.interfaces import ILanguage
    from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled  # noqa
    from plone.app.multilingual.interfaces import ITranslationManager


@unittest.skipUnless(
    PAM_INSTALLED, "plone.app.multilingual is installed by default only in Plone 5"
)  # NOQA
class TestTranslationInfo(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title=u"Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title=u"Test document"
        )
        ITranslationManager(self.en_content).register_translation("es", self.es_content)

    def test_translation_info_includes_translations(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request), name=u"GET_application_json_@translations"
        )

        info = tinfo.reply()
        self.assertIn("items", info)
        self.assertEqual(1, len(info["items"]))

    def test_correct_translation_information(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request), name=u"GET_application_json_@translations"
        )

        info = tinfo.reply()
        tinfo_es = info["items"][0]
        self.assertEqual(self.es_content.absolute_url(), tinfo_es["@id"])
        self.assertEqual(
            ILanguage(self.es_content).get_language(), tinfo_es["language"]
        )


@unittest.skipUnless(
    PAM_INSTALLED, "plone.app.multilingual is installed by default only in Plone 5"
)  # NOQA
class TestLinkContentsAsTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title=u"Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title=u"Test document"
        )
        transaction.commit()

    def test_translation_linking_by_url(self):
        response = requests.post(
            "{}/@translations".format(self.en_content.absolute_url()),
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
            "{}/@translations".format(self.en_content.absolute_url()),
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
            "{}/@translations".format(self.en_content.absolute_url()),
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
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_already_translated_content_gives_400(self):
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()
        response = requests.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_inexistent_content_gives_400(self):
        response = requests.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": "http://this-content-does-not-exist"},
        )
        self.assertEqual(400, response.status_code)

    def test_get_translations_on_content_with_no_permissions(self):
        response = requests.post(
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"id": self.es_content.absolute_url()},
        )
        self.assertEqual(201, response.status_code)
        api.content.transition(self.en_content, "publish")
        transaction.commit()

        response = requests.get(
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
        )

        self.assertEqual(200, response.status_code)
        response = response.json()
        self.assertTrue(len(response["items"]) == 0)


@unittest.skipUnless(
    PAM_INSTALLED, "plone.app.multilingual is installed by default only in Plone 5"
)  # NOQA
class TestUnLinkContentTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title=u"Test document"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title=u"Test document"
        )
        ITranslationManager(self.en_content).register_translation("es", self.es_content)
        transaction.commit()

    def test_translation_unlinking_succeeds(self):
        response = requests.delete(
            "{}/@translations".format(self.en_content.absolute_url()),
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
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={},
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_untranslated_content_gives_400(self):
        ITranslationManager(self.en_content).remove_translation("es")
        transaction.commit()
        response = requests.delete(
            "{}/@translations".format(self.en_content.absolute_url()),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={"language": "es"},
        )
        self.assertEqual(400, response.status_code)


@unittest.skipUnless(
    PAM_INSTALLED, "plone.app.multilingual is installed by default only in Plone 5"
)  # NOQA
class TestCreateContentsAsTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title=u"Test document"
        )
        transaction.commit()

    def test_post_to_folder_creates_document_translated(self):
        response = requests.post(
            "{}/de".format(self.portal.absolute_url()),
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


@unittest.skipUnless(
    PAM_INSTALLED, "plone.app.multilingual is installed by default only in Plone 5"
)  # NOQA
class TestTranslationLocator(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.layer["request"]
        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title=u"Test document"
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
