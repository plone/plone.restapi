# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.restapi.types.utils import get_jsonschema_for_portal_type

import json
import transaction
import unittest


class TestServicesSchema(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.doc = self.portal[self.portal.invokeFactory(
            "Document", id="doc1", title="My Document")]
        transaction.commit()

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_get_schema_document(self):
        response = self.api_session.get(
            "{}/@schema".format(self.doc.absolute_url())
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("Content-Type"),
            "application/json+schema",
            "Sending a GET request to @schema endpoint should respond with "
            + 'Content-Type: "application/json+schema", not '
            + '"{}"'.format(response.headers.get("Content-Type")),
        )

        jsonschema = get_jsonschema_for_portal_type(
            'Document', self.doc, self.portal.REQUEST)
        self.assertEqual(
            json.loads(json.dumps(jsonschema)), response.json(),
            '@schema endpoint should return the JSON schema for given context')

    def test_schema_endpoint_only_accessible_for_authenticated_users(self):
        self.api_session.auth = ()
        response = self.api_session.get("{}/@schema".format(self.doc.absolute_url()))
        self.assertEqual(response.status_code, 401)
