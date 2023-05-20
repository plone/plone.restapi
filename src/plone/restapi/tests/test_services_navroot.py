# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import (
    PLONE_RESTAPI_DX_FUNCTIONAL_TESTING,
    PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING,
)
from plone.restapi.testing import RelativeSession
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from plone.app.layout.navigation.interfaces import INavigationRoot

import unittest
from plone import api
import transaction


class TestServicesNavroot(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.content.create(
            container=self.portal,
            id="news",
            title="News",
            type="Folder",
        )
        api.content.create(
            container=self.portal.news,
            id="document",
            title="Document",
            type="Document",
        )
        api.content.transition(obj=self.portal.news, transition="publish")
        api.content.transition(obj=self.portal.news.document, transition="publish")
        transaction.commit()

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

    def test_get_navroot(self):
        response = self.api_session.get(
            "/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal, self.layer["request"]), name="plone_portal_state"
        )

        self.assertIn("navroot", response.json())
        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(response.json()["@id"], self.portal_url + "/@navroot")

    def test_get_navroot_non_multilingual_navigation_root(self):
        """test that the navroot is computed correctly when a section
        implements INavigationRoot
        """
        alsoProvides(self.portal.news, INavigationRoot)
        transaction.commit()

        response = self.api_session.get(
            "/news/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.news, self.layer["request"]),
            name="plone_portal_state",
        )

        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["navroot"]["@id"],
            portal_state.navigation_root_url(),
        )

    def test_get_navroot_non_multilingual_navigation_root_content(self):
        """test that the navroot is computed correctly in a content inside a section
        that implements INavigationRoot
        """
        alsoProvides(self.portal.news, INavigationRoot)
        transaction.commit()

        response = self.api_session.get(
            "/news/document/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.news, self.layer["request"]),
            name="plone_portal_state",
        )

        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["navroot"]["@id"],
            portal_state.navigation_root_url(),
        )


class TestServicesNavrootMultilingual(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        api.content.create(
            container=self.portal.en,
            id="news",
            title="News",
            type="Folder",
        )
        api.content.create(
            container=self.portal.en.news,
            id="document",
            title="Document",
            type="Document",
        )
        api.content.transition(obj=self.portal.en.news, transition="publish")
        api.content.transition(obj=self.portal.en.news.document, transition="publish")

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

        transaction.commit()

    def test_get_navroot_site(self):
        response = self.api_session.get(
            "/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal, self.layer["request"]), name="plone_portal_state"
        )
        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["@id"],
            portal_state.navigation_root_url() + "/@navroot",
        )

    def test_get_navroot_language_folder(self):
        response = self.api_session.get(
            "/en/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.en, self.layer["request"]), name="plone_portal_state"
        )
        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["@id"],
            portal_state.navigation_root_url() + "/@navroot",
        )

    def test_get_navroot_language_content(self):
        response = self.api_session.get(
            "/en/news/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.en.news, self.layer["request"]),
            name="plone_portal_state",
        )
        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["navroot"]["@id"],
            portal_state.navigation_root_url(),
        )

    def test_get_navroot_non_multilingual_navigation_root(self):
        """test that the navroot is computed correctly when a section
        implements INavigationRoot
        """
        alsoProvides(self.portal.en.news, INavigationRoot)
        transaction.commit()

        response = self.api_session.get(
            "/en/news/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.en.news, self.layer["request"]),
            name="plone_portal_state",
        )
        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["navroot"]["@id"],
            portal_state.navigation_root_url(),
        )

    def test_get_navroot_non_multilingual_navigation_root_content(self):
        """test that the navroot is computed correctly in a content inside a section
        that implements INavigationRoot
        """
        alsoProvides(self.portal.en.news, INavigationRoot)
        transaction.commit()

        response = self.api_session.get(
            "/en/news/document/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.en.news, self.layer["request"]),
            name="plone_portal_state",
        )
        self.assertIn("navroot", response.json())

        self.assertEqual(
            response.json()["navroot"]["title"],
            portal_state.navigation_root_title(),
        )
        self.assertEqual(
            response.json()["navroot"]["@id"],
            portal_state.navigation_root_url(),
        )
