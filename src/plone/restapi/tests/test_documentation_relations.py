from plone import api
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.services.relations import api_relation_create
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.tests.test_documentation import TestDocumentationBase
from plone.restapi.tests.test_documentation import save_request_and_response_for_docs

import transaction


class TestRelationsDocumentation(TestDocumentationBase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        super().setUp()

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

    def tearDown(self):
        super().tearDown()

    def test_documentation_relations_get(self):
        if api_relation_create:
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

            """
            Query relations by UID
            """
            # relation name
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            save_request_and_response_for_docs("relations_get_relationname", response)

            # (sub set of relations for Anonymous)
            self.api_session.auth = None
            response = self.api_session.get(
                "/@relations?relation=comprisesComponentPart",
            )
            save_request_and_response_for_docs(
                "relations_get_relationname_anonymous", response
            )
            self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

            # source
            response = self.api_session.get(
                f"/@relations?source={self.doc1.UID()}",
            )
            save_request_and_response_for_docs("relations_get_source", response)

            # (sub set of relations for Anonymous)
            self.api_session.auth = None
            response = self.api_session.get(
                f"/@relations?source={self.doc1.UID()}",
            )
            save_request_and_response_for_docs(
                "relations_get_source_anonymous", response
            )
            self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

            # source and relation
            response = self.api_session.get(
                f"/@relations?source={self.doc1.UID()}&relation=comprisesComponentPart",
            )
            save_request_and_response_for_docs(
                "relations_get_source_and_relation", response
            )

            # target
            response = self.api_session.get(
                f"/@relations?target={self.doc1.UID()}",
            )
            save_request_and_response_for_docs("relations_get_target", response)

            """
            TODO Query relations by path
            """
