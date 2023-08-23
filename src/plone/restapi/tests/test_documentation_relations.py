from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.vocabularies.catalog import StaticCatalogVocabulary
from plone.restapi.services.relations import api_relation_create
from plone.restapi.services.relations.get import getStaticCatalogVocabularyQuery
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.tests.test_documentation import TestDocumentationBase
from plone.restapi.tests.test_documentation import save_request_and_response_for_docs
from zope.component import provideUtility
from zope.schema.interfaces import IVocabularyFactory

import transaction

try:
    from Products.CMFPlone.relationhelper import rebuild_relations
except ImportError:
    try:
        from collective.relationhelpers.api import rebuild_relations
    except ImportError:
        rebuild_relations = None


def ExamplesVocabularyFactory(context=None):
    return StaticCatalogVocabulary(
        {
            "portal_type": ["example"],
            "review_state": "published",
            "sort_on": "sortable_title",
        }
    )


class TestRelationsDocumentation(TestDocumentationBase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()

        if api_relation_create:
            self.doc1 = api.content.create(
                container=self.portal,
                type="Document",
                id="document",
                title="Test document 1",
            )
            api.content.transition(self.doc1, "publish")

            self.doc2 = api.content.create(
                container=self.portal,
                type="Document",
                id="document-2",
                title="Test document 2",
            )
            api.content.transition(self.doc2, "publish")

            self.doc3 = api.content.create(
                container=self.portal,
                type="Document",
                id="document-3",
                title="Test document 3",
            )

            transaction.commit()

            api_relation_create(
                source=self.doc1,
                target=self.doc2,
                relationship="comprisesComponentPart",
            )
            api_relation_create(
                source=self.doc1,
                target=self.doc3,
                relationship="comprisesComponentPart",
            )
            api_relation_create(
                source=self.doc1,
                target=self.doc3,
                relationship="relatedItems",
            )
            api_relation_create(
                source=self.doc2,
                target=self.doc1,
                relationship="relatedItems",
            )
            transaction.commit()

    def tearDown(self):
        super().tearDown()

    def test_documentation_GET_relations(self):
        if api_relation_create:
            self.assertEqual(
                set(
                    [
                        relationvalue.to_object
                        for relationvalue in api.relation.get(
                            source=self.doc1, relationship="comprisesComponentPart"
                        )
                    ]
                ),
                {self.doc2, self.doc3},
            )
            self.assertEqual(
                set(
                    [
                        relationvalue.to_object
                        for relationvalue in api.relation.get(
                            source=self.doc1, relationship="relatedItems"
                        )
                    ]
                ),
                {self.doc3},
            )

            """
            Stats of relations
            """
            response = self.api_session.get(
                "/@relations",
            )
            save_request_and_response_for_docs("relations_catalog_get_stats", response)

            self.assertEqual(response.status_code, 200)
            resp = response.json()
            self.assertIn("stats", resp)
            self.assertIn("broken", resp)
            self.assertEqual(resp["stats"]["comprisesComponentPart"], 2)
            self.assertEqual(resp["broken"], {})

            """
            Query relations
            """
            # relation name
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            save_request_and_response_for_docs("relations_get_relationname", response)
            resp = response.json()
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 2
            )
            self.assertIn(
                "UID", resp["relations"]["comprisesComponentPart"]["items"][0]["source"]
            )

            # relation name (sub set of relations for Anonymous)
            self.api_session.auth = None
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            save_request_and_response_for_docs(
                "relations_get_relationname_anonymous", response
            )
            resp = response.json()
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 1
            )  # not 2 as for admin
            self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

            # source by path
            response = self.api_session.get(
                "/@relations?source=/document",
            )
            save_request_and_response_for_docs("relations_get_source_by_path", response)
            resp = response.json()
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 2
            )
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 1)

            # source by uid
            response = self.api_session.get(
                f"/@relations?source={self.doc1.UID()}",
            )
            save_request_and_response_for_docs("relations_get_source_by_uid", response)

            # source by path (sub set of relations for Anonymous)
            self.api_session.auth = None
            response = self.api_session.get(
                "/@relations?source=/document",
            )
            save_request_and_response_for_docs(
                "relations_get_source_anonymous", response
            )
            resp = response.json()
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 1
            )  # subset of results for manager
            self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

            # source and relation
            response = self.api_session.get(
                "/@relations?source=/document&relation=comprisesComponentPart",
            )
            save_request_and_response_for_docs(
                "relations_get_source_and_relation", response
            )

            # target
            response = self.api_session.get(
                "/@relations?target=/document",
            )
            save_request_and_response_for_docs("relations_get_target", response)
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 1)

    def test_documentation_GET_relations_vocabulary(self):
        if api_relation_create:
            # Register named staticCatalogVocabulary
            factory = ExamplesVocabularyFactory  # ()
            provideUtility(
                factory, provides=IVocabularyFactory, name="comprisesComponentPart"
            )

            # Query relations
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )

            resp = response.json()
            # Is the vocabulary registered?
            self.assertEqual(
                getStaticCatalogVocabularyQuery("comprisesComponentPart"),
                {
                    "portal_type": ["example"],
                    "review_state": "published",
                    "sort_on": "sortable_title",
                },
            )
            # Is the vocabulary included in response?
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"][
                    "staticCatalogVocabularyQuery"
                ],
                {
                    "portal_type": ["example"],
                    "review_state": "published",
                    "sort_on": "sortable_title",
                },
            )

    def test_documentation_POST_relations(self):
        """
        Add relations
        """
        self.maxDiff = None

        if api_relation_create:
            response = self.api_session.get(
                "/@relations?relation=relatedItems",
            )
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 2)

            response = self.api_session.post(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": "/document-3",
                            "target": "/document",
                            "relation": "relatedItems",
                        },
                        {
                            "source": "/document-3",
                            "target": "/document-2",
                            "relation": "relatedItems",
                        },
                    ]
                },
            )
            save_request_and_response_for_docs("relations_post", response)

            response = self.api_session.get(
                "/@relations?relation=relatedItems",
            )
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 4)

            # Failing addition
            response = self.api_session.post(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": "/document",
                            "target": "/document-does-not-exist",
                            "relation": "comprisesComponentPart",
                        }
                    ]
                },
            )
            save_request_and_response_for_docs("relations_post_failure", response)
            resp = response.json()
            self.assertIn("failed", resp["error"])

            # Add by UID
            response = self.api_session.post(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": self.doc1.UID(),
                            "target": self.doc2.UID(),
                            "relation": "comprisesComponentPart",
                        },
                        {
                            "source": self.doc3.UID(),
                            "target": self.doc2.UID(),
                            "relation": "comprisesComponentPart",
                        },
                    ]
                },
            )
            save_request_and_response_for_docs("relations_post_with_uid", response)

    def test_documentation_POST_relations_anonymous(self):
        """
        Post relations
        """

        if api_relation_create:
            self.api_session.auth = None
            response = self.api_session.post(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": "/document",
                            "target": "/document-2",
                            "relation": "comprisesComponentPart",
                        }
                    ]
                },
            )
            self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

            save_request_and_response_for_docs("relations_post_anonyous", response)

            # Get relations and test that no relation is removed.
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            resp = response.json()
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 2
            )

    def test_documentation_DEL_relations_list(self):
        """
        Delete relations
        """
        self.maxDiff = None

        if api_relation_create:
            # Delete list by path and UID
            response = self.api_session.delete(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": "/document",
                            "target": "/document-2",
                            "relation": "comprisesComponentPart",
                        },
                        {
                            "source": self.doc1.UID(),
                            "target": self.doc3.UID(),
                            "relation": "comprisesComponentPart",
                        },
                    ]
                },
            )
            save_request_and_response_for_docs("relations_del_path_uid", response)

            # Get relations and test that the deleted relations are removed.
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            resp = response.json()

            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 0
            )  # instead of 2 before deletion

            # Failing deletion
            response = self.api_session.delete(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": "/document",
                            "target": "/dont-know-this-doc",
                            "relation": "comprisesComponentPart",
                        },
                        {
                            "source": "/doc-does-not-exist",
                            "target": "/document",
                            "relation": "comprisesComponentPart",
                        },
                    ]
                },
            )
            save_request_and_response_for_docs("relations_del_failure", response)
            resp = response.json()
            self.assertIn("error", resp)

    def test_documentation_DEL_relations_list_anonymous(self):
        """
        Delete relations
        """

        if api_relation_create:
            self.api_session.auth = None
            response = self.api_session.delete(
                "/@relations",
                json={
                    "items": [
                        {
                            "source": "/document",
                            "target": "/document-2",
                            "relation": "comprisesComponentPart",
                        }
                    ]
                },
            )
            self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

            save_request_and_response_for_docs("relations_del_anonymous", response)

            # Get relations and test that no relation is removed.
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            resp = response.json()
            self.assertEqual(
                resp["relations"]["comprisesComponentPart"]["items_total"], 2
            )

    def test_documentation_DEL_relations_by_relationship(self):
        """
        Delete relations
        """
        self.maxDiff = None

        if api_relation_create:

            response = self.api_session.get(
                "/@relations?relation=relatedItems",
            )
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 2)

            # Delete by relation name
            response = self.api_session.delete(
                "/@relations",
                json={"relation": "relatedItems"},
            )
            save_request_and_response_for_docs("relations_del_relationname", response)

            response = self.api_session.get(
                "/@relations?relation=relatedItems",
            )
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 0)

    def test_documentation_DEL_relations_by_source_or_target(self):
        """
        Delete relations
        """
        self.maxDiff = None

        if api_relation_create:
            # Delete by source
            response = self.api_session.delete(
                "/@relations",
                json={"source": "/document"},
            )
            save_request_and_response_for_docs("relations_del_source", response)

            response = self.api_session.get(
                "/@relations?relation=relatedItems",
            )
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 1)

            # Delete by target
            response = self.api_session.delete(
                "/@relations",
                json={"target": "/document"},
            )
            save_request_and_response_for_docs("relations_del_target", response)

            response = self.api_session.get(
                "/@relations?relation=relatedItems",
            )
            resp = response.json()
            self.assertEqual(resp["relations"]["relatedItems"]["items_total"], 0)

    def test_documentation_DEL_relations_bunch_combi(self):
        """
        Delete relations
        """
        self.maxDiff = None

        if api_relation_create:
            response = self.api_session.get(
                "/@relations",
            )
            resp = response.json()
            self.assertEqual(resp["stats"]["comprisesComponentPart"], 2)
            self.assertEqual(resp["stats"]["relatedItems"], 2)

            # Delete by combination of source and relation name
            response = self.api_session.delete(
                "/@relations",
                json={"source": "/document", "relation": "relatedItems"},
            )
            save_request_and_response_for_docs("relations_del_combi", response)

            response = self.api_session.get(
                "/@relations",
            )
            resp = response.json()
            self.assertEqual(resp["stats"]["comprisesComponentPart"], 2)
            self.assertEqual(resp["stats"]["relatedItems"], 1)

            # Delete by combination of target and relation name
            response = self.api_session.delete(
                "/@relations",
                json={"target": "/document", "relation": "relatedItems"},
            )
            save_request_and_response_for_docs("relations_del_combi", response)

            response = self.api_session.get(
                "/@relations",
            )
            resp = response.json()
            self.assertEqual(resp["stats"]["comprisesComponentPart"], 2)
            self.assertNotIn("relatedItems", resp["stats"])

    def test_documentation_POST_rebuild(self):
        if rebuild_relations:
            response = self.api_session.post("/@relations/rebuild")
            save_request_and_response_for_docs("relations_rebuild", response)

            response = self.api_session.post(
                "/@relations/rebuild",
                json={"flush": 1},
            )
            save_request_and_response_for_docs("relations_rebuild_with_flush", response)
