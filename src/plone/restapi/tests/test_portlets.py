# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

from plone.app.portlets.portlets import news

import transaction
import unittest


class TestServicesPortlets(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    default_portlets_managers = {
            'plone.leftcolumn',
            'plone.rightcolumn',
            'plone.footerportlets',
            'plone.dashboard1',
            'plone.dashboard2',
            'plone.dashboard3',
            'plone.dashboard4'
        }

    def check_reponse_all_portlets(self, path):
        response = self.api_session.get(path)
        self.assertEqual(response.status_code, 200)

        j = response.json()

        managers = set([x['manager'] for x in j])
        self.assertEqual(managers, self.default_portlets_managers)

        assert path + '/plone.' in j[0]['@id']

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder1 = createContentInContainer(
            self.portal, u"Folder", id=u"folder-1", title=u"Folder 1"
        )
        self.folder1_1 = createContentInContainer(
            self.folder1, u"Folder", id=u"folder-1-1", title=u"Folder 1 1"
        )
        self.folder1_2 = createContentInContainer(
            self.folder1, u"Folder", id=u"folder-1-2", title=u"Folder 1 2"
        )
        self.link1_3 = createContentInContainer(
            self.folder1, u"Link", id=u"folder-1-3", title=u"Link 1 3", url=u"http://www.google.com"
        )
        self.folder2 = createContentInContainer(
            self.portal, u"Folder", id=u"folder-2", title=u"Folder 2"
        )

        createContentInContainer(
            self.folder1, u"Document", id=u"doc1", title=u"A document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_portlets_service_working(self):
        response = self.api_session.get("/@portlets")
        self.assertEqual(response.status_code, 200)

    def test_portlets_service(self):
        self.check_reponse_all_portlets("/@portlets")

    def test_portlets_inexisting_manager(self):
        response = self.api_session.get("/@portlets/plone.inexisting")
        self.assertEqual(response.status_code, 500)

    def test_portlets_navigation_folder_not_exist(self):
        response = self.api_session.get("/folder-not-exist@portlets")
        self.assertEqual(response.status_code, 404)

    def test_portlets_navigation_folder(self):
        self.check_reponse_all_portlets("/folder-1/@portlets")

    def test_portlets_navigation_subfolder_inexisting(self):
        response = self.api_session.get("/folder-1/inexisting/@portlets")
        self.assertEqual(response.status_code, 404)

    def test_portlets_navigation_subfolder(self):
        self.check_reponse_all_portlets("/folder-1/folder-1-1/@portlets")

    ''' LEFT COLUMN
    '''
    def test_portlets_left_column_root(self):
        response = self.api_session.get("/@portlets/plone.leftcolumn")
        self.assertEqual(response.status_code, 200)

        j = response.json()
        self.assertEqual(j['portlets'][0]['navigationportlet']['items'][0], [])

    def test_portlets_left_column_folder(self):
        response = self.api_session.get("/folder-1/@portlets/plone.leftcolumn")
        self.assertEqual(response.status_code, 200)

        self.assertTrue('portlets' in response.json())
        portlets = response.json()['portlets']

        self.assertTrue(any(portlet['@type'] == 'portlets.Navigation' for portlet in portlets))

    def test_portlets_left_column_subfolder1(self):
        response = self.api_session.get("/folder-1/folder-1-1/@portlets/plone.leftcolumn")
        self.assertEqual(response.status_code, 200)

        j = response.json()
        self.assertEqual(len(j['portlets'][0]['navigationportlet']['items'][0]), 4)
        self.assertTrue(j['portlets'][0]['navigationportlet']['items'][0][0]['is_current'])
        self.assertFalse(j['portlets'][0]['navigationportlet']['items'][0][1]['is_current'])
        self.assertEqual(j['portlets'][0]['navigationportlet']['items'][0][2]['type'], 'link')

    def test_portlets_left_column_subfolder2(self):
        response = self.api_session.get("/folder-1/folder-1-2/@portlets/plone.leftcolumn")
        self.assertEqual(response.status_code, 200)

        j = response.json()
        self.assertEqual(len(j['portlets'][0]['navigationportlet']['items'][0]), 4)
        self.assertFalse(j['portlets'][0]['navigationportlet']['items'][0][0]['is_current'])
        self.assertTrue(j['portlets'][0]['navigationportlet']['items'][0][1]['is_current'])
        self.assertEqual(j['portlets'][0]['navigationportlet']['items'][0][2]['type'], 'link')
