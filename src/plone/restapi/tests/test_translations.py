# -*- coding: utf-8 -*-
from plone.restapi.testing import LP_INSTALLED
from plone.restapi.testing import PAM_INSTALLED
from unittest2 import TestCase

if LP_INSTALLED:
    from plone.restapi.tests.translations_linguaplone import TestLPTranslationInfo  # noqa
    from plone.restapi.tests.translations_linguaplone import TestLPLinkContentsAsTranslations  # noqa
    from plone.restapi.tests.translations_linguaplone import TestLPUnLinkContentTranslationsTestCase  # noqa

if PAM_INSTALLED:
    from plone.restapi.tests.translations_pam import TestTranslationInfo  # noqa
    from plone.restapi.tests.translations_pam import TestLinkContentsAsTranslations  # noqa
    from plone.restapi.tests.translations_pam import TestUnLinkContentTranslations      # noqa


class DummyTest(TestCase):

    def test_true(self):
        self.assertTrue(True)
