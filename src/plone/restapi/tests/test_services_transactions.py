from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestTransactionsEndpoint(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.endpoint_url = f"{self.portal_url}/@transactions"

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_get_datastructure(self):
        response = self.api_session.get(self.endpoint_url)
        data = response.json()

        keys = ["description", "id", "size", "time", "username"]

        for item in data:
            self.assertEqual(set(item), set(keys))

    def test_revert(self):
        response = self.api_session.patch(
            self.endpoint_url, json={"transaction_ids": [""]}
        )
        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.json(),
            {"message": "Transactions have been reverted successfully."},
        )
