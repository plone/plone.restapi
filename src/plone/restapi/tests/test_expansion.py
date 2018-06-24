# -*- coding: utf-8 -*-
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.testing import PAM_INSTALLED
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

import transaction
import unittest

if PAM_INSTALLED:
    from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled  # noqa
    from plone.app.multilingual.interfaces import ITranslationManager


class ExpandableElementFoo(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if expand:
            return {'foo': 'expanded'}
        else:
            return {'foo': 'collapsed'}


class ExpandableElementBar(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if expand:
            return {'bar': 'expanded'}
        else:
            return {'bar': 'collapsed'}


class TestExpansion(unittest.TestCase):

    def setUp(self):
        provideAdapter(
            ExpandableElementFoo,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name='foo'
        )
        provideAdapter(
            ExpandableElementBar,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name='bar'
        )

    def test_expansion_returns_collapsed_elements(self):
        request = TestRequest()
        self.assertEqual(
            {'@components': {'bar': 'collapsed', 'foo': 'collapsed'}},
            expandable_elements(None, request))

    def test_expansion_returns_expanded_element(self):
        request = TestRequest(form={'expand': 'foo'})
        self.assertEqual(
            {'@components': {'bar': 'collapsed', 'foo': 'expanded'}},
            expandable_elements(None, request))

    def test_expansion_returns_multiple_expanded_elements(self):
        request = TestRequest(form={'expand': 'foo,bar'})
        self.assertEqual(
            {'@components': {'bar': 'expanded', 'foo': 'expanded'}},
            expandable_elements(None, request))

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            ExpandableElementFoo,
            (Interface, IBrowserRequest),
            IExpandableElement,
            'foo')
        gsm.unregisterAdapter(
            ExpandableElementBar,
            (Interface, IBrowserRequest),
            IExpandableElement,
            'bar')


class TestExpansionFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder = createContentInContainer(
            self.portal, u'Folder',
            id=u'folder',
            title=u'Some Folder')
        transaction.commit()

    def test_actions_is_expandable(self):
        response = self.api_session.get('/folder')

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'actions',
            response.json().get('@components').keys()
        )

    def test_actions_expanded(self):
        response = self.api_session.get(
            '/folder',
            params={
                "expand": "actions"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            'object' in response.json()['@components']['actions']
        )
        self.assertTrue(
            'object_buttons' in response.json()['@components']['actions']
        )
        self.assertTrue(
            'portal_tabs' in response.json()['@components']['actions']
        )
        self.assertTrue(
            'site_actions' in response.json()['@components']['actions']
        )
        self.assertTrue(
            'user' in response.json()['@components']['actions']
        )

    def test_navigation_is_expandable(self):
        response = self.api_session.get('/folder')

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'navigation',
            response.json().get('@components').keys()
        )

    def test_navigation_expanded(self):
        response = self.api_session.get(
            '/folder',
            params={
                "expand": "navigation"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [
                {
                    u'title': u'Home',
                    u'@id': u'http://localhost:55001/plone',
                    u'description': u'',
                },
                {
                    u'title': u'Some Folder',
                    u'@id': u'http://localhost:55001/plone/folder',
                    u'description': u'',
                }
            ],
            response.json()['@components']['navigation']['items']
        )

    def test_navigation_expanded_with_depth(self):
        createContentInContainer(
            self.portal, u'Folder',
            id=u'folder2',
            title=u'Some Folder 2')
        subfolder1 = createContentInContainer(
            self.folder, u'Folder',
            id=u'subfolder1',
            title=u'SubFolder 1')
        createContentInContainer(
            self.folder, u'Folder',
            id=u'subfolder2',
            title=u'SubFolder 2')
        thirdlevelfolder = createContentInContainer(
            subfolder1, u'Folder',
            id=u'thirdlevelfolder',
            title=u'Third Level Folder')
        createContentInContainer(
            thirdlevelfolder, u'Folder',
            id=u'fourthlevelfolder',
            title=u'Fourth Level Folder')
        createContentInContainer(
            self.folder, u'Document',
            id=u'doc1',
            title=u'A document')
        transaction.commit()

        response = self.api_session.get(
            '/folder',
            params={
                "expand": "navigation",
                "expand.navigation.depth": 3
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            len(response.json()['@components']['navigation']['items']), 3
        )
        self.assertEqual(
            len(response.json()['@components']['navigation']['items'][1]['items']), 3 # noqa
        )
        self.assertEqual(
            len(response.json()['@components']['navigation']['items'][1]['items'][0]['items']), 1 # noqa
        )

    def test_breadcrumbs_is_expandable(self):
        response = self.api_session.get('/folder')

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'breadcrumbs',
            response.json().get('@components').keys()
        )

    def test_breadcrumbs_expanded(self):
        response = self.api_session.get(
            '/folder',
            params={
                "expand": "breadcrumbs"
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [
                {
                    u'title': u'Some Folder',
                    u'@id': u'http://localhost:55001/plone/folder'
                }
            ],
            response.json()['@components']['breadcrumbs']['items']
        )

    def test_workflow_is_expandable(self):
        response = self.api_session.get('/folder')

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'workflow',
            response.json().get('@components').keys()
        )

    def test_workflow_expanded(self):
        response = self.api_session.get(
            '/folder',
            params={
                "expand": "workflow"
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            u'http://localhost:55001/plone/folder/@workflow',
            response.json().get('@components').get('workflow').get('@id')
        )
        self.assertEqual(
            u'private',
            response.json()['@components']['workflow']['history'][0]['review_state']  # noqa
        )
        self.assertEqual(
            u'Private',
            response.json()['@components']['workflow']['history'][0]['title']
        )
        self.assertEqual(
            [
                {
                    u'@id': u'http://localhost:55001/plone/folder/@workflow/publish',  # noqa
                    u'title': u'Publish'
                },
                {
                    u'@id': u'http://localhost:55001/plone/folder/@workflow/submit',  # noqa
                    u'title': u'Submit for publication'
                }
            ],
            response.json()['@components']['workflow']['transitions']
        )


@unittest.skipUnless(PAM_INSTALLED, 'plone.app.multilingual is installed by default only in Plone 5')  # NOQA
class TestTranslationExpansionFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        alsoProvides(self.layer['request'], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal['en'], 'Document', title='Test document')
        self.es_content = createContentInContainer(
            self.portal['es'], 'Document', title='Test document')
        ITranslationManager(self.en_content).register_translation(
            'es', self.es_content)

        transaction.commit()

    def test_translations_is_expandable(self):
        response = self.api_session.get('/en/test-document')

        self.assertEqual(response.status_code, 200)
        self.assertIn(
            'translations',
            response.json().get('@components').keys()
        )

    def test_translations_expanded(self):
        response = self.api_session.get(
            '/en/test-document',
            params={
                "expand": "translations"
            }
        )

        self.assertEqual(response.status_code, 200)
        translation_dict = {
            '@id': self.es_content.absolute_url(),
            'language': 'es'
        }
        self.assertIn(
            translation_dict,
            response.json()['@components']['translations']['items']
        )
