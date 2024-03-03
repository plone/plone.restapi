# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getMultiAdapter

import unittest


class TestServicesSite(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})

    def test_get_site(self):
        response = self.api_session.get(
            "/@site",
        )

        self.assertEqual(response.status_code, 200)
        portal_state = getMultiAdapter(
            (self.portal, self.layer["request"]), name="plone_portal_state"
        )
        self.assertEqual(
            response.json()["plone.site_title"], portal_state.portal_title()
        )
        self.assertIn("plone.site_logo", response.json())
        self.assertIn("plone.robots_txt", response.json())
        self.assertIn("plone.allowed_sizes", response.json())
        self.assertIn("plone.available_languages", response.json())
        self.assertIn("plone.default_language", response.json())
        self.assertEqual(response.json()["plone.portal_timezone"], "UTC")
