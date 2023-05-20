from AccessControl.SecurityManagement import getSecurityManager
from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.relations import plone_api_content_get
from plone.restapi.services.relations import api_relation_create
from Products.CMFCore.permissions import ManagePortal
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
import plone.protect.interfaces
import logging


log = logging.getLogger(__name__)

try:
    from Products.CMFPlone.relationhelper import rebuild_relations
except ImportError:
    try:
        from collective.relationhelpers.api import rebuild_relations
    except ImportError:
        rebuild_relations = None


@implementer(IPublishTraverse)
class PostRelations(Service):
    """Create new relations."""

    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        self.sm = getSecurityManager()

    def publishTraverse(self, request, name):
        # Treat any path segments after /@relations as parameters
        self.params.append(name)
        return self

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        if not api_relation_create:
            raise NotImplementedError()

        data = json_body(self.request)

        # Rebuild relations with or without regenerating intIds
        if "rebuild" in self.params:
            if api.user.has_permission(ManagePortal):
                if rebuild_relations:
                    flush = True if data.get("flush", False) else False
                    try:
                        rebuild_relations(flush_and_rebuild_intids=flush)
                        print("*** Relations rebuild. flush:", flush)
                        return self.reply_no_content()
                    except Exception as e:
                        self.request.response.setStatus(500)
                        return dict(
                            error=dict(
                                # type="ImportError",
                                message=str(e),
                            )
                        )
                else:
                    self.request.response.setStatus(501)
                    return dict(
                        error=dict(
                            type="ImportError",
                            message="Relationhelpers not available. Install collective.relationhelpers or upgrade to Plone 6!",
                        )
                    )
            else:
                self.request.response.setStatus(403)
                return dict(
                    error=dict(
                        type="Forbidden",
                    )
                )

        failed_relations = []
        for relationdata in data["items"]:
            source_obj = plone_api_content_get(UID=relationdata["source"])
            if not source_obj:
                source_obj = plone_api_content_get(path=relationdata["source"])
            target_obj = plone_api_content_get(UID=relationdata["target"])
            if not target_obj:
                target_obj = plone_api_content_get(path=relationdata["target"])

            if not source_obj or not target_obj:
                msg = (
                    "Source and target not found."
                    if not source_obj and not target_obj
                    else "Source not found."
                    if not source_obj
                    else "Target not found."
                )
                msg = f"Failed on creating a relation. {msg}"
                log.error(f"{msg} {relationdata}")
                failed_relations.append((relationdata, msg))
                continue

            try:
                api_relation_create(
                    source=source_obj,
                    target=target_obj,
                    relationship=relationdata["relation"],
                )
            except Exception as e:
                msg = f"{type(e).__name__}: {str(e)}. Failed on creating a relation. source:{source_obj}, target: {target_obj}"
                log.error(f"{msg} {relationdata}")
                failed_relations.append((relationdata, msg))
                continue

        if len(failed_relations) > 0:
            return self._error(
                422,
                "Unprocessable Content",
                "Failed on creating relations",
                failed_relations,
            )

        return self.reply_no_content()

    def _error(self, status, type, message, failed=[]):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message, "failed": failed}}
