from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from Products.CMFCore.utils import getToolByName

import transaction
import unittest


class TestContentRulesNotActivated(unittest.TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])
        setup = getToolByName(self.portal, "portal_setup")
        if not setup.profileExists("plone.app.contentrules:uninstall"):
            self.skipTest("plone.app.contentrules without uninstall profile")
        setup.runAllImportStepsFromProfile("profile-plone.app.contentrules:uninstall")
        setup.unsetLastVersionForProfile("plone.app.contentrules:default")
        transaction.commit()
        self.api_session = RelativeSession(self.portal_url, test=self)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

    def tearDown(self):
        self.api_session.close()

    def test_controlpanel_not_listed(self):
        response = self.api_session.get("/@controlpanels")
        self.assertEqual(response.status_code, 200)
        names = [p["@id"].split("/")[-1] for p in response.json()]
        self.assertNotIn("content-rules", names)

    def test_controlpanel_404(self):
        response = self.api_session.get("/@controlpanels/content-rules")
        self.assertEqual(response.status_code, 404)

    def test_content_rules_404(self):
        response = self.api_session.get("/@content-rules")
        self.assertEqual(response.status_code, 404)

    def test_content_rules_404_without_layer(self):
        # Storage present, browser layer missing (upgrade not run yet).
        from plone.contentrules.engine.interfaces import IRuleStorage
        from zope.component import queryUtility

        setup = getToolByName(self.portal, "portal_setup")
        setup.runImportStepFromProfile(
            "profile-plone.app.contentrules:default",
            "componentregistry",
            run_dependencies=False,
        )
        transaction.commit()
        self.assertIsNotNone(queryUtility(IRuleStorage))
        response = self.api_session.get("/@content-rules")
        self.assertEqual(response.status_code, 404)
        response = self.api_session.get("/@controlpanels/content-rules")
        self.assertEqual(response.status_code, 404)

    def test_controlpanel_write_methods_404_for_unknown_panel(self):
        # DELETE needs a sub-path, otherwise it fails earlier with 400.
        for method in ("post", "patch", "delete"):
            response = getattr(self.api_session, method)(
                "/@controlpanels/content-rules/some-rule", json={}
            )
            self.assertEqual(response.status_code, 404, method)

    def test_write_methods_404_for_truly_unknown_panel(self):
        for method in ("post", "patch", "delete"):
            response = getattr(self.api_session, method)(
                "/@controlpanels/does-not-exist/x", json={}
            )
            self.assertEqual(response.status_code, 404, method)
