from Acquisition import aq_parent
from plone.dexterity.content import DexterityContent
from plone.dexterity.interfaces import IDexterityContent
from typing import List
from z3c.caching.interfaces import IPurgePaths
from zope.component import adapter
from zope.interface import implementer


CONTEXT_ENDPOINTS = [
    "/@actions",
    "/@breadcrumbs",
    "/@comments",
    "/@navigation",
]


PARENT_ENDPOINTS = [
    "/@navigation",
]


@implementer(IPurgePaths)
@adapter(IDexterityContent)
class RestAPIPurgePaths:
    """RestAPI paths to purge for content items."""

    TRAVERSAL_PREFIX: str = "/++api++"

    def __init__(self, context: DexterityContent):
        """Initialize RestAPIPurgePaths."""
        self.context = context

    def getRelativePaths(self) -> List[str]:
        """Return a list of paths that should be purged. The paths should be
        relative to the virtual hosting root, i.e. they should start with a
        '/'.

        These paths will be rewritten to incorporate virtual hosting if
        necessary.
        """
        prefix = self.TRAVERSAL_PREFIX
        base_path = f"/{self.context.virtual_url_path()}"
        paths = [f"{prefix}{base_path}"]

        # Add service endpoints for content
        for endpoint in CONTEXT_ENDPOINTS:
            path = f"{prefix}{base_path}{endpoint}"
            paths.append(path)

        # Process parent context
        parent = aq_parent(self.context)
        if parent is None:
            return paths

        base_path = f"/{parent.virtual_url_path()}"
        # Add service endpoints for parent
        for endpoint in PARENT_ENDPOINTS:
            path = f"{prefix}{base_path}{endpoint}".replace("//", "/")
            paths.append(path)
        return paths

    def getAbsolutePaths(self) -> List[str]:
        """Return a list of paths that should be purged. The paths should be
        relative to the domain root, i.e. they should start with a '/'.

        These paths will *not* be rewritten to incorporate virtual hosting.
        """
        return []
