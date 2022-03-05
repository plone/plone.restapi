from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession

import transaction
import unittest


class TestHistoryEndpoint(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory(
            "Document", id="doc_with_history", title="My Document"
        )
        self.doc = self.portal.doc_with_history
        self.doc.setTitle("Current version")

        api.content.transition(self.doc, "publish")

        self.endpoint_url = f"{self.doc.absolute_url()}/@history"

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_get_types(self):
        # Check if we have all history types in our test setup
        response = self.api_session.get(self.endpoint_url)
        data = response.json()

        types = [item["type"] for item in data]

        self.assertEqual({"versioning", "workflow"}, set(types))

    def test_get_datastructure(self):
        response = self.api_session.get(self.endpoint_url)
        data = response.json()

        actor_keys = ["@id", "id", "fullname", "username"]

        main_keys = ["action", "actor", "comments", "time", "transition_title", "type"]

        history_keys = main_keys + ["@id", "may_revert", "version"]

        workflow_keys = main_keys + ["review_state", "state_title"]

        for item in data:
            # Make sure we'll add tests when new history types are added.
            self.assertIn(item["type"], ["versioning", "workflow"])

            if item["type"] == "versioning":
                self.assertEqual(set(item), set(history_keys))
            else:
                self.assertEqual(set(item), set(workflow_keys))

            self.assertEqual(set(item["actor"]), set(actor_keys))

            self.assertIsNotNone(item["action"])

    def test_revert(self):
        url = f"{self.doc.absolute_url()}/@history"
        response = self.api_session.patch(url, json={"version": 0})
        self.assertEqual(response.status_code, 200)

        # My Document is the old title
        self.assertEqual(
            response.json(),
            {"message": "My Document has been reverted to revision 0."},
        )

    def test_time_field(self):
        url = f"{self.doc.absolute_url()}/@history"
        response = self.api_session.get(url)

        for item in response.json():
            self.assertTrue(isinstance(item["time"], str))

    def test_get_historical_link(self):
        # The @id field should link to @history/version.
        response = self.api_session.get(self.endpoint_url)
        data = response.json()

        for item in data:
            if item["type"] == "versioning":
                self.assertTrue(
                    item["@id"].endswith("@history/" + str(item["version"]))
                )
            else:
                self.assertNotIn("@id", list(item))

    def test_explicit_current(self):
        # Does version=current get the current version
        url = self.doc.absolute_url() + "/@history/current"
        response = self.api_session.get(url)
        self.assertEqual(response.json()["title"], "Current version")

    def test_previous_version(self):
        # Does version=0 get the older version?
        url = self.doc.absolute_url() + "/@history/0"
        response = self.api_session.get(url)
        self.assertEqual(response.json()["title"], "My Document")

    def test_no_sharing(self):
        url = self.doc.absolute_url() + "/@history/0"
        response = self.api_session.get(url)
        self.assertNotIn("sharing", response.json())


class TestHistoryEndpointEmptyOrInacessibleHistory(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def _disable_auto_versioning(self, content_type):
        portal_repository = self.portal.portal_repository
        types = list(portal_repository.getVersionableContentTypes())
        types.remove(content_type)
        portal_repository.setVersionableContentTypes(types)
        portal_repository.removePolicyFromContentType(content_type, "version_on_revert")

    def setUp(self):
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()

        login(self.portal, SITE_OWNER_NAME)

        # disabling auto versioning is necessary to have an empty revision
        # history
        self._disable_auto_versioning("Document")

        self.portal.invokeFactory(
            "Document", id="doc_with_empty_history", title="My Document"
        )
        self.doc = self.portal.doc_with_empty_history
        api.content.transition(self.doc, "publish")
        self.endpoint_url = f"{self.doc.absolute_url()}/@history"

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (TEST_USER_NAME, TEST_USER_PASSWORD)
        # forbid access to `workflowHistory`
        setRoles(self.portal, TEST_USER_ID, ["Reader", "Contributor"])
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_empty_or_inaccessible_full_history_returns_empty_list(self):
        url = self.doc.absolute_url() + "/@history"
        response = self.api_session.get(url)
        self.assertEqual([], response.json())


class TestHistoryEndpointTranslatedMessages(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.headers.update({"Accept-Language": "es"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.portal.invokeFactory(
            "Document", id="doc_with_history", title="My Document"
        )
        self.doc = self.portal.doc_with_history
        self.doc.setTitle("Current version")

        api.content.transition(self.doc, "publish")

        self.endpoint_url = f"{self.doc.absolute_url()}/@history"

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_actions_are_translated(self):
        url = self.doc.absolute_url() + "/@history"
        response = self.api_session.get(url)
        first_action = response.json()[-1]
        self.assertEqual("Crear", first_action["action"])

    def test_state_titles_are_translated(self):
        url = self.doc.absolute_url() + "/@history"
        response = self.api_session.get(url)
        first_action = response.json()[-1]
        self.assertEqual("Privado", first_action["state_title"])

    def test_transition_titles_are_translated(self):
        url = self.doc.absolute_url() + "/@history"
        response = self.api_session.get(url)
        first_action = response.json()[-1]
        self.assertEqual("Crear", first_action["transition_title"])
