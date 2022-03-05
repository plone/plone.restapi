from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import transaction
import unittest


class TestRegistry(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        registry = getUtility(IRegistry)
        record = Record(field.TextLine(title="Foo Bar"), "Lorem Ipsum")
        registry.records["foo.bar"] = record

        for counter in range(1, 100):
            record = Record(field.TextLine(title="Foo Bar"), "Lorem Ipsum")
            registry.records["foo.bar" + str(counter)] = record

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_get_registry_record(self):
        response = self.api_session.get("/@registry/foo.bar")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "Lorem Ipsum")

    def test_update_registry_record(self):
        registry = getUtility(IRegistry)
        payload = {"foo.bar": "lorem ipsum"}
        response = self.api_session.patch("/@registry", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(registry["foo.bar"], "lorem ipsum")

    def test_update_several_registry_records(self):
        registry = getUtility(IRegistry)
        record = Record(field.TextLine(title="Foo Bar Baz"), "Lorem Ipsum Dolor")
        registry.records["foo.bar.baz"] = record
        transaction.commit()
        payload = {"foo.bar": "lorem ipsum", "foo.bar.baz": "lorem ipsum dolor"}
        response = self.api_session.patch("/@registry", json=payload)
        transaction.commit()

        self.assertEqual(response.status_code, 204)
        self.assertEqual(registry["foo.bar"], "lorem ipsum")
        self.assertEqual(registry["foo.bar.baz"], "lorem ipsum dolor")

    def test_update_non_existing_registry_record(self):
        payload = {"foo.bar.baz": "lorem ipsum"}
        response = self.api_session.patch("/@registry", json=payload)
        self.assertEqual(response.status_code, 500)

    def test_get_listing(self):
        response = self.api_session.get("/@registry")

        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertIn("items", response)
        self.assertIn("batching", response)
        self.assertIn("next", response["batching"])
