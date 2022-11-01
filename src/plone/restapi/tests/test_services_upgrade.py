from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.factory import _DEFAULT_PROFILE

import transaction
import unittest


# Python 3 is only supported on 5.2+.
# This means you can not upgrade from 5.1 or earlier.
START_VERSION = "5200"


class TestUpgradeServiceFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.setup = getToolByName(self.portal, "portal_setup")
        self.setup.setLastVersionForProfile(_DEFAULT_PROFILE, START_VERSION)
        transaction.commit()
        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_upgrade(self):
        response = self.api_session.get("/@upgrade")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(results["@id"], f"{self.portal.absolute_url()}/@upgrade")
        self.assertTrue("versions" in results.keys())
        self.assertEqual(results["versions"]["instance"], START_VERSION)
        self.assertNotEqual(results["versions"]["fs"], results["versions"]["instance"])
        self.assertTrue("upgrade_steps" in results.keys())
        self.assertGreater(len(results["upgrade_steps"]), 0)

    def test_post_upgrade_dry_run(self):
        response = self.api_session.post("/@upgrade", json={"dry_run": True})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(results["@id"], f"{self.portal.absolute_url()}/@upgrade")
        self.assertTrue("report" in results.keys())
        self.assertTrue("versions" in results.keys())
        self.assertNotEqual(results["versions"]["fs"], results["versions"]["instance"])
        self.assertTrue(results["dry_run"])
        self.assertFalse(results["upgraded"])

    def test_post_upgrade(self):
        response = self.api_session.post("/@upgrade", json={"dry_run": False})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        self.assertEqual(results["@id"], f"{self.portal.absolute_url()}/@upgrade")
        self.assertTrue("report" in results.keys())
        self.assertTrue("versions" in results.keys())
        self.assertEqual(results["versions"]["fs"], results["versions"]["instance"])
        self.assertFalse(results["dry_run"])
        self.assertTrue(results["upgraded"])
