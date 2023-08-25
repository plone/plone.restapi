from plone.restapi.search.utils import unflatten_dotted_dict

import unittest


class TestUnflattenDottedDict(unittest.TestCase):
    def test_unflattens_dotted_dict(self):
        dct = {"a.b.X": 1, "a.b.Y": 2, "a.foo": 3, "bar": 4}
        self.assertEqual(
            {"a": {"b": {"X": 1, "Y": 2}, "foo": 3}, "bar": 4},
            unflatten_dotted_dict(dct),
        )

    def test_works_on_empty_dict(self):
        self.assertEqual({}, unflatten_dotted_dict({}))

    def test_works_with_list_values(self):
        dct = {"path.query": ["foo", "bar"], "path.depth": 2}
        self.assertEqual(
            {"path": {"query": ["foo", "bar"], "depth": 2}}, unflatten_dotted_dict(dct)
        )

    def test_leaves_regular_keys_untouched(self):
        dct = {"foo": 1, "bar": 2}
        self.assertEqual(dct, unflatten_dotted_dict(dct))
