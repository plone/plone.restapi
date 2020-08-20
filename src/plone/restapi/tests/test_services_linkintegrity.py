# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.dexterity.utils import createContentInContainer
from plone.registry.interfaces import IRegistry
from plone.restapi.testing import PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from plone.uuid.interfaces import IUUID
from Products.CMFPlone.interfaces import IEditingSchema
from z3c.relationfield import RelationValue
from zope.component import getUtility
from zope.event import notify
from zope.intid.interfaces import IIntIds
from zope.lifecycleevent import ObjectModifiedEvent

import transaction
import unittest


class TestServicesNavigation(unittest.TestCase):

    layer = PLONE_RESTAPI_BLOCKS_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer["app"]
        self.portal = self.layer["portal"]
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ["Manager"])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({"Accept": "application/json"})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        self.doc1 = createContentInContainer(
            self.portal, u"Document", id=u"doc-1", title=u"First document"
        )
        self.doc2 = createContentInContainer(
            self.portal, u"Document", id=u"doc-2", title=u"Second document"
        )
        transaction.commit()

    def tearDown(self):
        self.api_session.close()

    def test_return_no_breaches_by_default(self):
        response = self.api_session.get("/doc-2/@linkintegrity")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_return_right_breaches_for_reference_field(self):
        intids = getUtility(IIntIds)
        self.doc1.relatedItems = [RelationValue(intids.getId(self.doc2))]
        notify(ObjectModifiedEvent(self.doc1))
        transaction.commit()

        response = self.api_session.get("/doc-2/@linkintegrity")
        breaches = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(breaches, [])
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0]["target"]["uid"], IUUID(self.doc2))
        self.assertEqual(breaches[0]["target"]["@id"], self.doc2.absolute_url())
        self.assertEqual(len(breaches[0]["sources"]), 1)
        self.assertEqual(breaches[0]["sources"][0]["uid"], IUUID(self.doc1))
        self.assertEqual(breaches[0]["sources"][0]["@id"], self.doc1.absolute_url())

    def test_do_not_return_breaches_if_check_is_disabled(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(IEditingSchema, prefix="plone")
        settings.enable_link_integrity_checks = False
        intids = getUtility(IIntIds)
        self.doc1.relatedItems = [RelationValue(intids.getId(self.doc2))]
        notify(ObjectModifiedEvent(self.doc1))
        transaction.commit()

        response = self.api_session.get("/doc-2/@linkintegrity")
        breaches = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(breaches, [])

    def test_return_right_breaches_for_blocks(self):
        response = self.api_session.get("/doc-2/@linkintegrity")
        breaches = response.json()
        self.assertEqual(breaches, [])

        uid = IUUID(self.doc2)
        self.api_session.patch(
            "/doc-1",
            json={
                "blocks": {
                    "uuid1": {
                        "@type": "text",
                        "text": {
                            "blocks": [{"text": "This is a link to second doc "}],
                            "entityMap": {
                                "0": {
                                    "data": {
                                        "href": "../resolveuid/{}".format(uid),
                                        "rel": "nofollow",
                                        "url": "../resolveuid/{}".format(uid),
                                    },
                                    "mutability": "MUTABLE",
                                    "type": "LINK",
                                }
                            },
                        },
                    }
                }
            },
        )
        transaction.commit()

        response = self.api_session.get("/doc-2/@linkintegrity")
        breaches = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(breaches, [])
        self.assertEqual(len(breaches), 1)
        self.assertEqual(breaches[0]["target"]["uid"], IUUID(self.doc2))
        self.assertEqual(breaches[0]["target"]["@id"], self.doc2.absolute_url())
        self.assertEqual(len(breaches[0]["sources"]), 1)
        self.assertEqual(breaches[0]["sources"][0]["uid"], IUUID(self.doc1))
        self.assertEqual(breaches[0]["sources"][0]["@id"], self.doc1.absolute_url())
