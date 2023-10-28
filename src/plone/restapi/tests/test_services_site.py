# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getMultiAdapter

import unittest

IS_PLONE4 = False

try:
    from Products.CMFPlone.interfaces import IImagingSchema  # noqa
    from Products.CMFPlone.interfaces import ISiteSchema  # noqa
except ImportError:
    IS_PLONE4 = True


class TestServicesSite(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})

    def test_get_site_title(self):
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

    @unittest.skipIf(
        IS_PLONE4,
        "The information can only be extracted from the ISiteSchema and IImagingSchema values in registry, which are only available in Plone 5",
    )  # NOQA
    def test_get_site_other(self):
        response = self.api_session.get(
            "/@site",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("plone.site_logo", response.json())
        self.assertIn("plone.robots_txt", response.json())
        self.assertIn("plone.allowed_sizes", response.json())
