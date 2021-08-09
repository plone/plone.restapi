# -*- coding: utf-8 -*-
from datetime import datetime
from DateTime import DateTime
from plone.app.dexterity.behaviors.metadata import IPublication
from plone.registry.interfaces import IRegistry
from plone.restapi.interfaces import IFieldDeserializer
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from transaction import commit
from z3c.form.interfaces import IDataManager
from zope.component import getMultiAdapter
from zope.component import getUtility

import unittest
import os
import time


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
        DateTime.localZone = lambda cls=None, ltm=None: tz

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
        if "TZ" in os.environ:
            del os.environ["TZ"]
        time.tzset()

        from DateTime import DateTime

        DateTime.localZone = self.DT_orig_localZone

        from plone.dexterity import content

        content._zone = self._orig_content_zone
        content.FLOOR_DATE = DateTime(1970, 0)
        content.CEILING_DATE = DateTime(2500, 0)

        registry = getUtility(IRegistry)
        registry["plone.portal_timezone"] = "UTC"
        registry["plone.available_timezones"] = ["UTC"]

    def test_effective_date_deserialization_localized(self):
        self.portal.invokeFactory("Document", id="doc-test", title="Test Document")
        field_name = "effective"
        field = IPublication.get(field_name)
        serializer = getMultiAdapter(
            (field, self.portal["doc-test"], self.request), IFieldDeserializer
        )
        value = serializer("2015-05-20T10:39:54.361+00")
        self.assertEqual(datetime(2015, 12, 20, 12, 39, 54, 361000), value)

    def test_effective_date_serialization_localized(self):
        self.portal.invokeFactory("Document", id="doc-test", title="Test Document")
        doc = self.portal["doc-test"]
        field_name = "effective"
        field = IPublication.get(field_name)
        deserializer = getMultiAdapter((field, doc, self.request), IFieldDeserializer)
        value = deserializer("2015-05-20T10:39:54.361+00")

        #  set value on content
        dm = getMultiAdapter((doc, field), IDataManager)
        dm.set(value)

        serializer = getMultiAdapter((field, doc, self.request), IFieldSerializer)
        self.assertEqual(doc.effective().timezone(), "Europe/Rome")
        self.assertEqual(serializer(), "2015-05-20T10:39:00+00:00")
