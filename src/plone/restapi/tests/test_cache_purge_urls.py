from Acquisition import aq_base
from Acquisition import Explicit
from plone.restapi.cache.paths import RestAPIPurgePaths
from plone.testing.zca import UNIT_TESTING
from Products.CMFCore.interfaces import IContentish
from Products.CMFDynamicViewFTI.interfaces import IBrowserDefault
from zope.interface import implementer

import unittest


@implementer(IContentish)
class FauxNonContent(Explicit):
    def __init__(self, name=None):
        self.__name__ = name
        self.__parent__ = None  # may be overridden by acquisition

    def getId(self):
        return self.__name__

    def virtual_url_path(self):
        parent = aq_base(self.__parent__)
        if parent is not None:
            return f"{parent.virtual_url_path()}/{self.__name__}"
        else:
            return self.__name__

    def getPhysicalPath(self):
        return ("",)

    def getParentNode(self):
        return FauxNonContent("folder")


@implementer(IBrowserDefault)
class FauxContent(FauxNonContent):
    portal_type = "testtype"

    def defaultView(self):
        return "default-view"


class TestRestAPIPurgePaths(unittest.TestCase):
    layer = UNIT_TESTING

    def test_no_parent(self):
        context = FauxNonContent("foo")
        purger = RestAPIPurgePaths(context)

        self.assertEqual(
            [
                "/++api++/foo",
                "/++api++/foo/@actions",
                "/++api++/foo/@breadcrumbs",
                "/++api++/foo/@comments",
                "/++api++/foo/@navigation",
            ],
            list(purger.getRelativePaths()),
        )
        self.assertEqual([], list(purger.getAbsolutePaths()))

    def test_parent(self):
        context = FauxContent("foo").__of__(FauxContent("bar"))
        purger = RestAPIPurgePaths(context)
        self.assertEqual(
            [
                "/++api++/bar/foo",
                "/++api++/bar/foo/@actions",
                "/++api++/bar/foo/@breadcrumbs",
                "/++api++/bar/foo/@comments",
                "/++api++/bar/foo/@navigation",
                "/++api++/bar/@navigation",
            ],
            list(purger.getRelativePaths()),
        )
        self.assertEqual([], list(purger.getAbsolutePaths()))
