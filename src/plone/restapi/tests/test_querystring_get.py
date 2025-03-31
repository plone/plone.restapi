from plone.app.testing import PLONE_RESTAPI_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
import unittest

class TestQuerystringGet(unittest.TestCase):

    layer = PLONE_RESTAPI_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]
        self.api_session = RelativeSession(self.portal.absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})

    def test_vocabularies_permission_filtering(self):
        response = self.api_session.get("/@querystring")
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # Assert that a sensitive vocabulary is filtered out
        self.assertNotIn('plone.app.vocabularies.Users', result['indexes'])
        self.assertNotIn('plone.app.vocabularies.Groups', result['indexes'])
        
        # Assert that public vocabularies are still present
        self.assertIn('plone.app.vocabularies.Keywords', result['indexes'])

    def tearDown(self):
        self.api_session.close()
