# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestServicesPortlets(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder = createContentInContainer(
            self.portal, u"Folder", id=u"folder", title=u"Some Folder"
        )
        self.folder2 = createContentInContainer(
            self.portal, u"Folder", id=u"folder2", title=u"Some Folder 2"
        )
        self.subfolder1 = createContentInContainer(
            self.folder, u"Folder", id=u"subfolder1", title=u"SubFolder 1"
        )
        self.subfolder2 = createContentInContainer(
            self.folder, u"Folder", id=u"subfolder2", title=u"SubFolder 2"
        )
        self.thirdlevelfolder = createContentInContainer(
            self.subfolder1,
            u"Folder",
            id=u"thirdlevelfolder",
            title=u"Third Level Folder",
        )
        self.fourthlevelfolder = createContentInContainer(
            self.thirdlevelfolder,
            u"Folder",
            id=u"fourthlevelfolder",
            title=u"Fourth Level Folder",
        )
        createContentInContainer(
            self.folder, u"Document", id=u"doc1", title=u"A document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_portlets_service(self):
        response = self.api_session.get("/@portlets")
        self.assertEqual(response.status_code, 200)

        j = response.json()

        managers = set([x['manager'] for x in j])
        self.assertEqual(managers, set([
            'plone.leftcolumn',
            'plone.rightcolumn',
            'plone.footerportlets',
            'plone.dashboard1',
            'plone.dashboard2',
            'plone.dashboard3',
            'plone.dashboard4'
        ]))

        assert '/plone/@portlets/plone.' in j[0]['@id']

    def test_portlet_navigation_simple(self):
        response = self.api_session.get("/@portlets")
        self.assertEqual(response.status_code, 200)

        j = response.json()

        managers = set([x['manager'] for x in j])
        self.assertEqual(managers, set([
            'plone.leftcolumn',
            'plone.rightcolumn',
            'plone.footerportlets',
            'plone.dashboard1',
            'plone.dashboard2',
            'plone.dashboard3',
            'plone.dashboard4'
        ]))

        assert '/plone/@portlets/plone.' in j[0]['@id']

    def test_default_portlets_left_column(self):
        base = "/folder/subfolder1/thirdlevelfolder"
        base_url = self.portal_url + base

        response = self.api_session.get(base + "/@portlets/plone.leftcolumn")
        self.assertEqual(response.status_code, 200)

        j = response.json()

        self.assertEqual(j['@id'],
                         self.portal_url + base + '/@portlets/plone.leftcolumn'
                         )
        self.assertEqual(j['manager'], 'plone.leftcolumn')
        portlets = j['portlets']

        self.assertEqual(len(portlets), 1)

        navportlet = portlets[0]
        self.assertEqual(navportlet['@id'],
                         base_url +
                         '/@portlets/plone.leftcolumn/navigation')
        self.assertEqual(navportlet['@type'], 'portlets.Navigation')
        self.assertEqual(navportlet['portlet_category'], 'context')
        self.assertEqual(navportlet['portlet_manager'], 'plone.leftcolumn')

        tree = navportlet['navigationportlet']

        self.assertEqual(tree['title'], 'Navigation')
        self.assertEqual(tree['url'], self.portal_url + '/sitemap')

        self.assertEqual(len(tree['items']), 3)

        self.assertEqual(tree['items'][1],
                         {'@id': self.portal_url + '/folder/subfolder2',
                          'description': '',
                          'href': self.portal_url + '/folder/subfolder2',
                          'icon': '',
                          'is_current': False,
                          'is_folderish': True,
                          'is_in_path': False,
                          'items': [],
                          'normalized_id': 'subfolder2',
                          'review_state': 'private',
                                          'thumb': '',
                                          'title': 'SubFolder 2',
                                          'type': 'folder'})

        self.assertEqual(tree['items'][2],
                         {'@id': self.portal_url + '/folder/doc1',
                          'description': '',
                          'href': self.portal_url + '/folder/doc1',
                          'icon': '',
                          'is_current': False,
                          'is_folderish': False,
                          'is_in_path': False,
                          'items': [],
                          'normalized_id': 'doc1',
                          'review_state': 'private',
                          'thumb': '',
                          'title': 'A document',
                          'type': 'document'})

        self.assertEqual(tree['items'][0],

                         {'@id': self.portal_url + '/folder/subfolder1',
                          'description': '',
                          'href': self.portal_url + '/folder/subfolder1',
                          'icon': '',
                          'is_current': False,
                          'is_folderish': True,
                          'is_in_path': True,
                          'items': [{'@id': base_url,
                                     'description': '',
                                     'href': base_url,
                                     'icon': '',
                                     'is_current': True,
                                     'is_folderish': True,
                                     'is_in_path': False,
                                     'items': [
                                         {'@id': base_url + '/fourthlevelfolder',
                                          'description': '',
                                          'href': base_url + '/fourthlevelfolder',
                                          'icon': '',
                                          'is_current': False,
                                          'is_folderish': True,
                                          'is_in_path': False,
                                          'items': [],
                                          'normalized_id': 'fourthlevelfolder',
                                          'review_state': 'private',
                                          'thumb': '',
                                          'title': 'Fourth Level Folder',
                                          'type': 'folder'}],
                                     'normalized_id': 'thirdlevelfolder',
                                     'review_state': 'private',
                                     'thumb': '',
                                     'title': 'Third Level Folder',
                                     'type': 'folder'}],
                          'normalized_id': 'subfolder1',
                          'review_state': 'private',
                          'thumb': '',
                          'title': 'SubFolder 1',
                          'type': 'folder'}
                         )
