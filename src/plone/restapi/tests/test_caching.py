from ..testing import PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING
from ..testing import RelativeSession
from plone.app.testing import applyProfile
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.caching.interfaces import ICacheSettings
from plone.registry.interfaces import IRegistry
from zope.component import getUtility
from zope.globalrequest import setRequest

import transaction
import unittest


@unittest.skipIf(
    PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING is None,
    "Test needs plone.app.caching>3.0.0a13",
    # condition and fallback can be removed in a Plone 6.0 only scenario
)
class TestProfileWithCachingRestAPI(unittest.TestCase):
    """This test aims to exercise the caching operations expected from the
    `with-caching-proxy` profile for supported restapi calls.
    """

    if PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING is not None:
        layer = PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        setRequest(self.portal.REQUEST)

        applyProfile(self.portal, "plone.app.caching:with-caching-proxy")

        self.registry = getUtility(IRegistry)
        self.cacheSettings = self.registry.forInterface(ICacheSettings)
        self.cacheSettings.enabled = True

        # some test content
        setRoles(self.portal, TEST_USER_ID, ("Manager",))

        self.portal.invokeFactory("Folder", "f1")
        self.portal["f1"].title = "Folder one"
        self.portal.portal_workflow.doActionFor(self.portal["f1"], "publish")

        self.portal["f1"].invokeFactory("Folder", "f2")
        self.portal["f1"]["f2"].title = "Folder one sub one"
        self.portal.portal_workflow.doActionFor(self.portal["f1"]["f2"], "publish")

        self.portal.invokeFactory("Collection", "c")
        self.portal["c"].title = "A Collection"
        self.portal.portal_workflow.doActionFor(self.portal["c"], "publish")

        transaction.commit()

        # restapi test session
        self.api_session = RelativeSession(self.layer["portal"].absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})

    def test_restapi_actions(self):
        # plone.content.dynamic for plone.restapi.services.actions.get.ActionsGet
        response = self.api_session.get("/f1/f2/@actions")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_breadcrumbs(self):
        # plone.content.dynamic for plone.restapi.services.breadcrumbs.get.BreadcrumbsGet
        response = self.api_session.get("/f1/f2/@breadcrumbs")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_comments(self):
        # plone.content.itemView for plone.restapi.services.discussion.conversation.CommentsGet
        response = self.api_session.get("/f1/f2/@comments")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.itemView")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.weakCaching"
        )

    def test_restapi_content(self):
        # plone.content.dynamic for plone.restapi.services.content.get.ContentGet
        response = self.api_session.get("/f1/f2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_navigation(self):
        # plone.content.dynamic for plone.restapi.services.navigation.get.NavigationGet
        response = self.api_session.get("/f1/f2/@navigation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_querystring(self):
        # plone.content.dynamic for plone.restapi.services.querystring.get.QueryStringGet
        response = self.api_session.get("/@querystring")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_search(self):
        # plone.content.dynamic for plone.restapi.services.search.get.SearchGet
        response = self.api_session.get("/@search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )


@unittest.skipIf(
    PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING is None,
    "Test needs plone.app.caching>3.0.0a13",
    # condition and fallback can be removed in a Plone 6.0 only scenario
)
class TestProfileWithoutCachingRestAPI(unittest.TestCase):
    """This test aims to exercise the caching operations expected from the
    `without-caching-proxy` profile for supported restapi calls.
    """

    if PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING is not None:
        layer = PLONE_RESTAPI_CACHING_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        setRequest(self.portal.REQUEST)

        applyProfile(self.portal, "plone.app.caching:without-caching-proxy")

        self.registry = getUtility(IRegistry)
        self.cacheSettings = self.registry.forInterface(ICacheSettings)
        self.cacheSettings.enabled = True

        # some test content
        setRoles(self.portal, TEST_USER_ID, ("Manager",))

        self.portal.invokeFactory("Folder", "f1")
        self.portal["f1"].title = "Folder one"
        self.portal.portal_workflow.doActionFor(self.portal["f1"], "publish")

        self.portal["f1"].invokeFactory("Folder", "f2")
        self.portal["f1"]["f2"].title = "Folder one sub one"
        self.portal.portal_workflow.doActionFor(self.portal["f1"]["f2"], "publish")

        self.portal.invokeFactory("Collection", "c")
        self.portal["c"].title = "A Collection"
        self.portal.portal_workflow.doActionFor(self.portal["c"], "publish")

        transaction.commit()

        # restapi test session
        self.api_session = RelativeSession(self.layer["portal"].absolute_url())
        self.api_session.headers.update({"Accept": "application/json"})

    def test_restapi_actions(self):
        # plone.content.dynamic for plone.restapi.services.actions.get.ActionsGet
        response = self.api_session.get("/f1/f2/@actions")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_breadcrumbs(self):
        # plone.content.dynamic for plone.restapi.services.breadcrumbs.get.BreadcrumbsGet
        response = self.api_session.get("/f1/f2/@breadcrumbs")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_comments(self):
        # plone.content.itemView for plone.restapi.services.discussion.conversation.CommentsGet
        response = self.api_session.get("/f1/f2/@comments")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.itemView")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.weakCaching"
        )

    def test_restapi_content(self):
        # plone.content.dynamic for plone.restapi.services.content.get.ContentGet
        response = self.api_session.get("/f1/f2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_navigation(self):
        # plone.content.dynamic for plone.restapi.services.navigation.get.NavigationGet
        response = self.api_session.get("/f1/f2/@navigation")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_querystring(self):
        # plone.content.dynamic for plone.restapi.services.querystring.get.QueryStringGet
        response = self.api_session.get("/@querystring")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )

    def test_restapi_search(self):
        # plone.content.dynamic for plone.restapi.services.search.get.SearchGet
        response = self.api_session.get("/@search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["X-Cache-Rule"], "plone.content.dynamic")
        self.assertEqual(
            response.headers["X-Cache-Operation"], "plone.app.caching.terseCaching"
        )
