from plone.contentrules.engine.interfaces import IRuleStorage
from zExceptions import NotFound
from zope.component import queryMultiAdapter
from zope.component import queryUtility


def ensure_rules_activated(context, request):
    """Raise NotFound unless content rules are activated in this site.

    Activated means: the rule storage exists and the management view is
    available for this request (the add-on browser layer is active).
    """
    if queryUtility(IRuleStorage) is None:
        raise NotFound("Content rules are not activated in this site.")
    if queryMultiAdapter((context, request), name="manage-content-rules") is None:
        raise NotFound("Content rules are not activated in this site.")
