from DateTime import DateTime
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from transaction import commit
from zope.component import getMultiAdapter
from zope.component import getUtility

import os
import time
import unittest


class TestPublicationFields(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):

        self.portal = self.layer["portal"]
        self.request = self.layer["request"]

        tz = "Europe/Rome"
        os.environ["TZ"] = tz
        time.tzset()

        # Patch DateTime's timezone for deterministic behavior.
        self.DT_orig_localZone = DateTime.localZone
        self.DT_orig_calcTimezoneName = DateTime._calcTimezoneName
        DateTime.localZone = lambda cls=None, ltm=None: tz
        DateTime._calcTimezoneName = lambda self, x, ms: tz

        from plone.dexterity import content

        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)
        self._orig_content_zone = content._zone
        content._zone = "GMT+2"

        registry = getUtility(IRegistry)
        registry["plone.portal_timezone"] = tz
        registry["plone.available_timezones"] = [tz]

        self.app = self.layer["app"]
        self.portal = self.layer["portal"]

        commit()

    def tearDown(self):
        os.environ["TZ"] = "UTC"
        time.tzset()

        from DateTime import DateTime

        DateTime.localZone = self.DT_orig_localZone
        DateTime._calcTimezoneName = self.DT_orig_calcTimezoneName

        from plone.dexterity import content

        content._zone = self._orig_content_zone
        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)

        registry = getUtility(IRegistry)
        registry["plone.portal_timezone"] = "UTC"
        registry["plone.available_timezones"] = ["UTC"]

    def test_effective_date_deserialization_localized(self):
        self.portal.invokeFactory("Document", id="doc-test", title="Test Document")
        doc = self.portal["doc-test"]
        deserializer = getMultiAdapter(
            (self.portal["doc-test"], self.request), IDeserializeFromJson
        )
        deserializer(data={"effective": "2015-05-20T10:39:54.361+00"})
        self.assertEqual(str(doc.effective_date), "2015/05/20 12:39:00 Europe/Rome")

    def test_effective_date_serialization_localized(self):
        self.portal.invokeFactory("Document", id="doc-test", title="Test Document")
        doc = self.portal["doc-test"]
        doc.effective_date = DateTime("2015/05/20 12:39:00 Europe/Rome")

        serializer = getMultiAdapter((doc, self.request), ISerializeToJson)
        data = serializer()
        self.assertEqual(data["effective"], "2015-05-20T10:39:00+00:00")
