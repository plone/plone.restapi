# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_AT_LP_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_AT_LP_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.component import getMultiAdapter

import requests
import transaction


class TestLPTranslationInfo(TestCase):

    layer = PLONE_RESTAPI_AT_LP_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        lsf = getMultiAdapter(
            (self.portal, self.request),
            name='language-setup-folders'
        )
        lsf()

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        self.en_content.addTranslationReference(self.es_content)

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
        self.assertEqual(self.es_content.Language(), tinfo_es['language'])


class TestLPLinkContentsAsTranslations(TestCase):
    layer = PLONE_RESTAPI_AT_LP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        lsf = getMultiAdapter(
            (self.portal, self.request),
            name='language-setup-folders'
        )
        lsf()

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
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
        self.assertIn(
            self.es_content.Language(),
            self.en_content.getTranslations(review_state=False).keys())

    def test_calling_endpoint_without_id_gives_400(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
            },
        )
        self.assertEqual(400, response.status_code)

    def test_calling_endpoint_with_invalid_id_gives_400(self):
        response = requests.post(
            '{}/@translations'.format(self.en_content.absolute_url()),
            headers={'Accept': 'application/json'},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
            json={
                'id': 'http://server.com/this-content-does-not-exist'
            },
        )
        self.assertEqual(400, response.status_code)


class TestLPUnLinkContentTranslationsTestCase(TestCase):
    layer = PLONE_RESTAPI_AT_LP_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        # self.portal.portal_languages.addSupportedLanguage('en')
        # self.portal.portal_languages.addSupportedLanguage('es')
        #  Setup the language root folders
        login(self.portal, SITE_OWNER_NAME)
        lsf = getMultiAdapter(
            (self.portal, self.request),
            name='language-setup-folders'
        )
        lsf()

        en_id = self.portal.en.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.en_content = self.portal.en.get(en_id)
        es_id = self.portal.es.invokeFactory(
            id='test-document',
            type_name='Document',
            title='Test document'
        )
        self.es_content = self.portal.es.get(es_id)
        self.en_content.addTranslationReference(self.es_content)
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
        self.assertNotIn(
            self.es_content.Language(),
            self.en_content.getTranslations(review_state=False).keys())

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
        self.en_content.removeTranslation("es")
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
