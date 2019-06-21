# -*- coding: utf-8 -*-
from freezegun import freeze_time
import freezegun
import time
import unittest


class TestTimeFreezing(unittest.TestCase):

    def test_freezegun_provides_original_time_functions(self):
        """This test guards against future API changes in freezegun.
        """
        # These module globals in freezegun.api provide access to the
        # original time functions.
        self.assertTrue(hasattr(freezegun.api, 'real_time'))
        self.assertTrue(hasattr(freezegun.api, 'real_gmtime'))

        # Before freezing time, they should be references to the
        # real time functions
        self.assertTrue(freezegun.api.real_time is time.time)
        self.assertTrue(freezegun.api.real_gmtime is time.gmtime)

        # After freezing, we expect them to differ
        with freeze_time("2016-10-21 19:00:00"):
            self.assertFalse(freezegun.api.real_time is time.time)
            self.assertFalse(freezegun.api.real_gmtime is time.gmtime)
