from plone.app.redirector.interfaces import IRedirectionStorage
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getUtility


import transaction
import unittest


class TestRedirector(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        # Create contents
        self.portal.invokeFactory("Folder", id="folder", title="Folderish")
        folder = self.portal.folder
        folder.invokeFactory("Folder", id="sub_folder", title="Another Folderish")
        folder.invokeFactory("Document", id="archive", title="My Document")

        # Add redirection from parent to a child
        storage = getUtility(IRedirectionStorage)
        storage.add(
            "/".join(folder.getPhysicalPath()),
            "/".join(folder.archive.getPhysicalPath()),
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_redirection_loop(self):
        url = self.portal.folder.sub_folder.absolute_url()

        # A request to a invalid service should return 404
        response = self.api_session.get(f"{url}/@service_not_found")
        self.assertEqual(response.status_code, 404)
