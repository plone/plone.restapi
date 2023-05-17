from pkg_resources import get_distribution
from pkg_resources import parse_version
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

import requests
import transaction
import unittest


linkintegrity_version = get_distribution("plone.app.linkintegrity").version
if parse_version(linkintegrity_version) >= parse_version("3.0.dev0"):
    NEW_LINKINTEGRITY = True
else:
    NEW_LINKINTEGRITY = False


class TestContentDelete(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        setRoles(self.portal, TEST_USER_ID, ["Member"])
        login(self.portal, SITE_OWNER_NAME)
        self.doc1 = self.portal[
            self.portal.invokeFactory("Document", id="doc1", title="My Document")
        ]
        transaction.commit()

    def test_delete_content_succeeds(self):
        response = requests.delete(
            self.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(SITE_OWNER_NAME, SITE_OWNER_PASSWORD),
        )
        self.assertEqual(204, response.status_code)
        transaction.begin()
        self.assertNotIn("doc1", self.portal.objectIds())

    def test_delete_content_returns_401_unauthorized(self):
        response = requests.delete(
            self.doc1.absolute_url(),
            headers={"Accept": "application/json"},
            auth=(TEST_USER_NAME, TEST_USER_PASSWORD),
        )
        self.assertEqual(401, response.status_code)
