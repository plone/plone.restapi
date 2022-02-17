from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName

import transaction
import unittest


class TestTransactionsServiceFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        self.request = self.portal.REQUEST
        self.catalog = getToolByName(self.portal, "portal_catalog")

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_get_transactions(self):
        response = self.api_session.get("/@transactions")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers.get("Content-Type"), "application/json")

        results = response.json()
        # transaction log is always empty when using zodb temp storage (for testing)
        self.assertEqual(results, [])
