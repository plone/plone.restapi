from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from AccessControl.SpecialUsers import nobody
from AccessControl.ZopeGuards import get_safe_globals
from AccessControl.ZopeGuards import guarded_getattr
from RestrictedPython import compile_restricted
from zExceptions import Unauthorized

import plone.restapi  # noqa: F401 -- make sure json is not made public
import unittest


class Protected:
    security = ClassSecurityInfo()
    text = '"secret"'

    security.declareProtected("Manage portal", "write")

    def write(self, text):
        self.text = text

    security.declareProtected("Manage portal", "read")

    def read(self):
        return self.text


InitializeClass(Protected)


class TestRestrictedJson(unittest.TestCase):
    def setUp(self):
        newSecurityManager(None, nobody)
        self.obj = Protected()

    def tearDown(self):
        noSecurityManager()

    def run_restricted(self, code):
        globs = get_safe_globals()
        globs["_getattr_"] = guarded_getattr
        globs["obj"] = self.obj
        exec(compile_restricted(code, "<test>", "exec"), globs)
        return globs.get("result")

    def test_import_json_not_allowed(self):
        with self.assertRaises(Unauthorized):
            self.run_restricted("import json")

    def test_dump_not_allowed(self):
        with self.assertRaises(Unauthorized):
            self.run_restricted("import json\njson.dump('pwned', obj)")
        self.assertEqual(self.obj.text, '"secret"')

    def test_load_not_allowed(self):
        with self.assertRaises(Unauthorized):
            self.run_restricted("import json\nresult = json.load(obj)")

    def test_from_import_dump_not_allowed(self):
        with self.assertRaises(Unauthorized):
            self.run_restricted("from json import dump")
