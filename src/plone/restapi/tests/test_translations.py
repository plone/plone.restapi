# -*- coding: utf-8 -*-
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


@unittest.skipUnless(PAM_INSTALLED, 'plone.app.multilingual is installed by default only in Plone 5')  # NOQA
class TestTranslationInfo(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal['en'], 'Document', title='Test document')
        self.es_content = createContentInContainer(
            self.portal['es'], 'Document', title='Test document')
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)

    def test_translation_info_includes_translations(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request),
            name=u'GET_application_json_@translations')

        info = tinfo.reply()
        self.assertIn('translations', info)
        self.assertEqual(1, len(info['translations']))

    def test_correct_translation_information(self):
        tinfo = getMultiAdapter(
            (self.en_content, self.request),
            name=u'GET_application_json_@translations')

        info = tinfo.reply()
        tinfo_es = info['translations'][0]
        self.assertEqual(
            self.es_content.absolute_url(),
            tinfo_es['@id'])
        self.assertEqual(
            ILanguage(self.es_content).get_language(),
            tinfo_es['language'])


@unittest.skipUnless(PAM_INSTALLED, 'plone.app.multilingual is installed by default only in Plone 5')  # NOQA
class TestLinkContentsAsTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal['en'], 'Document', title='Test document')
        self.es_content = createContentInContainer(
            self.portal['es'], 'Document', title='Test document')
        transaction.commit()

    def test_translation_linking_succeeds(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "id": self.es_content.absolute_url(),
            },
        )
        self.assertEqual(201, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        for language, translation in manager.get_translations():
            if language == ILanguage(self.es_content).get_language():
                self.assertEqual(translation, self.es_content)

    def test_calling_endpoint_without_id_gives_400(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
            },
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_already_translated_content_gives_400(self):
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)
        transaction.commit()
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'id': self.es_content.absolute_url()
            },
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_inexistent_content_gives_400(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'id': 'http://this-content-does-not-exist',
            },
        )
        self.assertEqual(400, response.status_code)


@unittest.skipUnless(PAM_INSTALLED, 'plone.app.multilingual is installed by default only in Plone 5')  # NOQA
class TestUnLinkContentTranslations(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal['en'], 'Document', title='Test document')
        self.es_content = createContentInContainer(
            self.portal['es'], 'Document', title='Test document')
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)
        transaction.commit()

    def test_translation_unlinking_succeeds(self):
        response = requests.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "language": "es",
            },
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        manager = ITranslationManager(self.en_content)
        self.assertNotIn(
            ILanguage(self.es_content).get_language(),
            manager.get_translations().keys())

    def test_calling_endpoint_without_language_gives_400(self):
        response = requests.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
            },
        )
        self.assertEqual(400, response.status_code)

    def test_calling_with_an_untranslated_content_gives_400(self):
        ITranslationManager(self.en_content).remove_translation("es")
        transaction.commit()
        response = requests.delete(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                "language": "es",
            },
        )
        self.assertEqual(400, response.status_code)
