from datetime import date
from datetime import time
from datetime import timedelta
from DateTime import DateTime
from persistent.list import PersistentList
from persistent.mapping import PersistentMapping
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest import TestCase
from z3c.relationfield.relation import RelationValue
from zope.component import getUtility
from zope.i18nmessageid import MessageFactory
from zope.intid.interfaces import IIntIds

import json
import Missing


class TestJsonCompatibleConverters(TestCase):
    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def test_None(self):
        self.assertEqual(None, json_compatible(None))
        self.assertEqual("null", json.dumps(json_compatible(None)))

    def test_error_when_type_unknown(self):
        err_regex = (
            r"^No converter for making <object object at [^>]*>"
            + r" \(<(class|type) \'object\'>\) JSON compatible.$"
        )

        with self.assertRaisesRegex(TypeError, err_regex):
            json_compatible(object())

        with self.assertRaisesRegex(TypeError, err_regex):
            json_compatible({"foo": [object()]})

    def test_True(self):
        self.assertEqual(True, json_compatible(True))
        self.assertEqual("true", json.dumps(json_compatible(True)))

    def test_False(self):
        self.assertEqual(False, json_compatible(False))
        self.assertEqual("false", json.dumps(json_compatible(False)))

    def test_unicode(self):
        self.assertEqual("foo", json_compatible("foo"))
        self.assertIsInstance(json_compatible("foo"), str)
        self.assertEqual('"foo"', json.dumps(json_compatible("foo")))

    def test_unicode_with_umlaut(self):
        self.assertEqual("Hall\xf6chen", json_compatible("Hall\xf6chen"))
        self.assertEqual(
            '"Hall\\u00f6chen"', json.dumps(json_compatible("Hall\xf6chen"))
        )

    def test_string_is_converted_to_unicode(self):
        # Standard library JSON works with unicode.
        self.assertEqual("foo", json_compatible("foo"))
        self.assertIsInstance(json_compatible("foo"), str)
        self.assertEqual('"foo"', json.dumps(json_compatible("foo")))

    def test_string_with_umlaut(self):
        # Standard library JSON works with unicode.
        self.assertEqual("Hall\xf6chen", json_compatible("Hallöchen"))
        self.assertEqual('"Hall\\u00f6chen"', json.dumps(json_compatible("Hallöchen")))

    def test_int(self):
        self.assertEqual(42, json_compatible(42))
        self.assertIsInstance(json_compatible(42), int)
        self.assertEqual("42", json.dumps(json_compatible(42)))

    def test_long(self):
        def _long(val):
            return int(val)

        self.assertEqual(_long(10), json_compatible(_long(10)))
        self.assertIsInstance(json_compatible(_long(10)), int)
        self.assertEqual("10", json.dumps(json_compatible(_long(10))))

    def test_float(self):
        self.assertEqual(1.4, json_compatible(1.4))
        self.assertIsInstance(json_compatible(1.4), float)
        self.assertEqual("1.4", json.dumps(json_compatible(1.4)))

    def test_list(self):
        self.assertEqual(["foo"], json_compatible(["foo"]))
        self.assertEqual('["foo"]', json.dumps(json_compatible(["foo"])))
        self.assertIsInstance(
            json_compatible(["foo"])[0],
            str,
            "List values should be converted recursively.",
        )

    def test_persistent_list(self):
        value = PersistentList(["foo"])
        self.assertEqual(["foo"], json_compatible(value))
        self.assertEqual('["foo"]', json.dumps(json_compatible(value)))
        self.assertIsInstance(
            json_compatible(value)[0],
            str,
            "PersistentList values should be converted" " recursively.",
        )

    def test_tuple(self):
        # Tuples are converted to list (json would do that anyway and
        # it is easier to implement it with map).
        self.assertEqual(["foo", None], json_compatible(("foo", None)))
        self.assertEqual('["foo"]', json.dumps(json_compatible(("foo",))))
        self.assertIsInstance(
            json_compatible(("foo",))[0],
            str,
            "Tuple values should be converted recursively.",
        )

    def test_frozenset(self):
        self.assertEqual(
            [[1, 1], [2, 2]], sorted(json_compatible(frozenset([(1, 1), (2, 2)])))
        )

    def test_set(self):
        self.assertEqual([[1, 1], [2, 2]], sorted(json_compatible({(1, 1), (2, 2)})))

    def test_dict(self):
        self.assertEqual(
            {"foo": True, "bar": None, "baz": 3},
            json_compatible({"foo": True, "bar": None, "baz": 3}),
        )
        self.assertEqual('{"foo": "bar"}', json.dumps(json_compatible({"foo": "bar"})))
        self.assertIsInstance(
            json_compatible(list({"foo": "bar"})[0]),
            str,
            "Dict keys should be converted recursively.",
        )
        self.assertIsInstance(
            json_compatible(list({"foo": "bar"}.values())[0]),
            str,
            "Dict values should be converted recursively.",
        )

    def test_dict_empty(self):
        self.assertEqual({}, json_compatible({}))
        self.assertEqual("{}", json.dumps(json_compatible({})))

    def test_persistent_mapping(self):
        value = PersistentMapping({"foo": "bar"})
        self.assertEqual({"foo": "bar"}, json_compatible(value))
        self.assertEqual('{"foo": "bar"}', json.dumps(json_compatible(value)))
        self.assertIsInstance(
            json_compatible(list(value)[0]),
            str,
            "Dict keys should be converted recursively.",
        )
        self.assertIsInstance(
            json_compatible(list(value.values())[0]),
            str,
            "Dict values should be converted recursively.",
        )

    def test_python_datetime(self):
        value = DateTime("2015/11/23 19:45:55.649027 GMT+3").asdatetime()
        self.assertEqual("2015-11-23T16:45:55+00:00", json_compatible(value))
        self.assertEqual(
            '"2015-11-23T16:45:55+00:00"', json.dumps(json_compatible(value))
        )

    def test_zope_DateTime(self):
        value = DateTime("2015/11/23 19:45:55.649027 GMT+3")
        self.assertEqual("2015-11-23T16:45:55+00:00", json_compatible(value))
        self.assertEqual(
            '"2015-11-23T16:45:55+00:00"', json.dumps(json_compatible(value))
        )

    def test_date(self):
        value = date(2015, 11, 23)
        self.assertEqual("2015-11-23", json_compatible(value))
        self.assertEqual('"2015-11-23"', json.dumps(json_compatible(value)))

    def test_time(self):
        value = time(19, 45, 55)
        self.assertEqual("19:45:55", json_compatible(value))
        self.assertEqual('"19:45:55"', json.dumps(json_compatible(value)))

    def test_timedelta(self):
        self.assertEqual(9.58, json_compatible(timedelta(seconds=9.58)))

    def test_broken_relation_value(self):
        self.assertEqual(None, json_compatible(RelationValue(12345)))

    def test_relation_value(self):
        portal = self.layer["portal"]
        doc1 = portal[
            portal.invokeFactory(
                "DXTestDocument",
                id="doc1",
                title="Document 1",
                description="Description",
            )
        ]
        intids = getUtility(IIntIds)
        self.assertEqual(
            {
                "@id": "http://nohost/plone/doc1",
                "@type": "DXTestDocument",
                "title": "Document 1",
                "description": "Description",
                "review_state": "private",
            },
            json_compatible(RelationValue(intids.getId(doc1))),
        )

    def test_i18n_message(self):
        _ = MessageFactory("plone.restapi.tests")
        msg = _("message_id", default="default message")
        self.assertEqual("default message", json_compatible(msg))

    def test_missing_value(self):
        self.assertEqual(None, json_compatible(Missing.Value))
