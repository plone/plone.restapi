from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.serializer.expansion import expandable_elements
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getGlobalSiteManager
from zope.component import provideAdapter
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import TestRequest
from zope.publisher.interfaces.browser import IBrowserRequest

import transaction
import unittest


class ExpandableElementFoo:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if expand:
            return {"foo": "expanded"}
        else:
            return {"foo": "collapsed"}


class ExpandableElementBar:
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if expand:
            return {"bar": "expanded"}
        else:
            return {"bar": "collapsed"}


class TestExpansion(unittest.TestCase):
    def setUp(self):
        provideAdapter(
            ExpandableElementFoo,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name="foo",
        )
        provideAdapter(
            ExpandableElementBar,
            adapts=(Interface, IBrowserRequest),
            provides=IExpandableElement,
            name="bar",
        )

    def test_expansion_returns_collapsed_elements(self):
        request = TestRequest()
        self.assertEqual(
            {"@components": {"bar": "collapsed", "foo": "collapsed"}},
            expandable_elements(None, request),
        )

    def test_expansion_returns_expanded_element(self):
        request = TestRequest(form={"expand": "foo"})
        self.assertEqual(
            {"@components": {"bar": "collapsed", "foo": "expanded"}},
            expandable_elements(None, request),
        )

    def test_expansion_returns_multiple_expanded_elements(self):
        request = TestRequest(form={"expand": "foo,bar"})
        self.assertEqual(
            {"@components": {"bar": "expanded", "foo": "expanded"}},
            expandable_elements(None, request),
        )

    def tearDown(self):
        gsm = getGlobalSiteManager()
        gsm.unregisterAdapter(
            ExpandableElementFoo,
            (Interface, IBrowserRequest),
            IExpandableElement,
            "foo",
        )
        gsm.unregisterAdapter(
            ExpandableElementBar,
            (Interface, IBrowserRequest),
            IExpandableElement,
            "bar",
        )


class TestExpansionFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.folder = createContentInContainer(
            self.portal, "Folder", id="folder", title="Some Folder"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_actions_is_expandable(self):
        response = self.api_session.get("/folder")

        self.assertEqual(response.status_code, 200)
        self.assertIn("actions", list(response.json().get("@components")))

    def test_actions_expanded(self):
        response = self.api_session.get("/folder", params={"expand": "actions"})

        self.assertEqual(response.status_code, 200)
        self.assertTrue("object" in response.json()["@components"]["actions"])
        self.assertTrue("object_buttons" in response.json()["@components"]["actions"])
        self.assertTrue("portal_tabs" in response.json()["@components"]["actions"])
        self.assertTrue("site_actions" in response.json()["@components"]["actions"])
        self.assertTrue("user" in response.json()["@components"]["actions"])

    def test_navigation_is_expandable(self):
        response = self.api_session.get("/folder")

        self.assertEqual(response.status_code, 200)
        self.assertIn("navigation", list(response.json().get("@components")))

    def test_navigation_expanded(self):
        response = self.api_session.get("/folder", params={"expand": "navigation"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [
                {
                    "title": "Home",
                    "@id": self.portal_url + "",
                    "description": "",
                    "review_state": None,
                    "items": [],
                },
                {
                    "title": "Some Folder",
                    "@id": self.portal_url + "/folder",
                    "description": "",
                    "review_state": "private",
                    "items": [],
                },
            ],
            response.json()["@components"]["navigation"]["items"],
        )

    def test_navigation_expanded_with_depth(self):
        createContentInContainer(
            self.portal, "Folder", id="folder2", title="Some Folder 2"
        )
        subfolder1 = createContentInContainer(
            self.folder, "Folder", id="subfolder1", title="SubFolder 1"
        )
        createContentInContainer(
            self.folder, "Folder", id="subfolder2", title="SubFolder 2"
        )
        thirdlevelfolder = createContentInContainer(
            subfolder1, "Folder", id="thirdlevelfolder", title="Third Level Folder"
        )
        createContentInContainer(
            thirdlevelfolder,
            "Folder",
            id="fourthlevelfolder",
            title="Fourth Level Folder",
        )
        createContentInContainer(self.folder, "Document", id="doc1", title="A document")
        transaction.commit()

        response = self.api_session.get(
            "/folder", params={"expand": "navigation", "expand.navigation.depth": 3}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["@components"]["navigation"]["items"]), 3)
        self.assertEqual(
            len(response.json()["@components"]["navigation"]["items"][1]["items"]),
            3,  # noqa
        )
        self.assertEqual(
            len(
                response.json()["@components"]["navigation"]["items"][1]["items"][0][
                    "items"
                ]
            ),
            1,  # noqa
        )

    def test_breadcrumbs_is_expandable(self):
        response = self.api_session.get("/folder")

        self.assertEqual(response.status_code, 200)
        self.assertIn("breadcrumbs", list(response.json().get("@components")))

    def test_breadcrumbs_expanded(self):
        response = self.api_session.get("/folder", params={"expand": "breadcrumbs"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [
                {
                    "title": "Some Folder",
                    "@id": self.portal_url + "/folder",
                }
            ],
            response.json()["@components"]["breadcrumbs"]["items"],
        )

    def test_workflow_is_expandable(self):
        response = self.api_session.get("/folder")

        self.assertEqual(response.status_code, 200)
        self.assertIn("workflow", list(response.json().get("@components")))

    def test_workflow_expanded(self):
        response = self.api_session.get("/folder", params={"expand": "workflow"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            self.portal_url + "/folder/@workflow",
            response.json().get("@components").get("workflow").get("@id"),
        )
        self.assertEqual(
            "private",
            response.json()["@components"]["workflow"]["history"][0][
                "review_state"
            ],  # noqa
        )
        self.assertEqual(
            "Private",
            response.json()["@components"]["workflow"]["history"][0]["title"],
        )
        self.assertEqual(
            [
                {
                    "@id": self.portal_url + "/folder/@workflow/publish",  # noqa
                    "title": "Publish",
                },
                {
                    "@id": self.portal_url + "/folder/@workflow/submit",  # noqa
                    "title": "Submit for publication",
                },
            ],
            response.json()["@components"]["workflow"]["transitions"],
        )

    def test_types_is_expandable(self):
        response = self.api_session.get("/folder")

        self.assertEqual(response.status_code, 200)
        self.assertIn("types", list(response.json().get("@components")))

    def test_types_expanded(self):
        response = self.api_session.get("/folder", params={"expand": "types"})

        self.assertEqual(response.status_code, 200)

        # XXX: Note: The @types endpoint currently doesn't conform to JSON-LD
        # because it's directly returning a list, and does not have an @id
        # property.

        base_url = self.portal.absolute_url()

        self.assertEqual(
            [
                {
                    "@id": "/".join((base_url, "@types/Collection")),
                    "addable": True,
                    "title": "Collection",
                },
                {
                    "@id": "/".join((base_url, "@types/DXTestDocument")),
                    "addable": True,
                    "title": "DX Test Document",
                },
                {
                    "@id": "/".join((base_url, "@types/Event")),
                    "addable": True,
                    "title": "Event",
                },
                {
                    "@id": "/".join((base_url, "@types/File")),
                    "addable": True,
                    "title": "File",
                },
                {
                    "@id": "/".join((base_url, "@types/Folder")),
                    "addable": True,
                    "title": "Folder",
                },
                {
                    "@id": "/".join((base_url, "@types/Image")),
                    "addable": True,
                    "title": "Image",
                },
                {
                    "@id": "/".join((base_url, "@types/Link")),
                    "addable": True,
                    "title": "Link",
                },
                {
                    "@id": "/".join((base_url, "@types/News Item")),
                    "addable": True,
                    "title": "News Item",
                },
                {
                    "@id": "/".join((base_url, "@types/Document")),
                    "addable": True,
                    "title": "Page",
                },
            ],
            response.json().get("@components").get("types"),
        )


class TestTranslationExpansionFunctional(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_PAM_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        alsoProvides(self.layer["request"], IPloneAppMultilingualInstalled)
        login(self.portal, SITE_OWNER_NAME)
        self.en_content = createContentInContainer(
            self.portal["en"], "Document", title="Test document"
        )
        self.en_folder = createContentInContainer(
            self.portal["en"], "Folder", title="Test folder"
        )
        self.es_content = createContentInContainer(
            self.portal["es"], "Document", title="Test document"
        )
        ITranslationManager(self.en_content).register_translation("es", self.es_content)

        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_translations_is_expandable(self):
        response = self.api_session.get("/en/test-document")

        self.assertEqual(response.status_code, 200)
        self.assertIn("translations", list(response.json().get("@components")))

    def test_translations_expanded(self):
        response = self.api_session.get(
            "/en/test-document", params={"expand": "translations"}
        )

        self.assertEqual(response.status_code, 200)
        translation_dict = {"@id": self.es_content.absolute_url(), "language": "es"}
        self.assertIn(
            translation_dict, response.json()["@components"]["translations"]["items"]
        )

    def test_expansions_no_fullobjects_do_not_modify_id(self):
        response = self.api_session.get(
            "/en/test-folder", params={"expand": "translations"}
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["@id"], self.en_folder.absolute_url())
