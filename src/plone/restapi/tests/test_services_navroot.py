# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import (
    PLONE_RESTAPI_DX_FUNCTIONAL_TESTING,
    PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING,
)
from plone.restapi.testing import RelativeSession
from zope.component import getMultiAdapter

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
        self.assertEqual(
            response.json()["title"], portal_state.navigation_root_title()
        )
        self.assertEqual(response.json()["@id"], self.portal_url)


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
            type="Document",
        )
        api.content.transition(obj=self.portal.en.news, transition="publish")

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
        self.assertEqual(
            response.json()["title"], portal_state.navigation_root_title()
        )
        self.assertEqual(
            response.json()["@id"], portal_state.navigation_root_url()
        )

    def test_get_navroot_language_folder(self):
        response = self.api_session.get(
            "/en/@navroot",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal.en, self.layer["request"]), name="plone_portal_state"
        )
        self.assertEqual(
            response.json()["title"], portal_state.navigation_root_title()
        )
        self.assertEqual(
            response.json()["@id"], portal_state.navigation_root_url()
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
        self.assertEqual(
            response.json()["title"], portal_state.navigation_root_title()
        )
        self.assertEqual(
            response.json()["@id"], portal_state.navigation_root_url()
        )
