from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.relations import plone_api_content_get
from plone.restapi.services.relations import api_relation_delete
from zope.interface import alsoProvides
import plone.protect.interfaces
import logging


log = logging.getLogger(__name__)


class DeleteRelations(Service):
    """Delete relations."""

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        if not api_relation_delete:
            raise NotImplementedError()

        data = json_body(self.request)

        failed_relations = []
        # List of single relations
        if data.get("items", None):
            for relationdata in data["items"]:
                # UIDs provided?
                source_obj = plone_api_content_get(UID=relationdata["source"])
                target_obj = plone_api_content_get(UID=relationdata["target"])
                # Or maybe path provided?
                if not source_obj:
                    source_obj = plone_api_content_get(path=relationdata["source"])
                if not target_obj:
                    target_obj = plone_api_content_get(path=relationdata["target"])
                # Source or target not found by UID or path
                if not source_obj or not target_obj:
                    msg = (
                        "Source and target not found."
                        if not source_obj and not target_obj
                        else "Source not found."
                        if not source_obj
                        else "Target not found."
                    )
                    msg = f"Failed on deleting a relation. {msg}"
                    log.error(f"{msg} {relationdata}")
                    failed_relations.append((relationdata, msg))
                    continue

                try:
                    api_relation_delete(
                        source=source_obj,
                        target=target_obj,
                        relationship=relationdata["relation"],
                    )
                except Exception as e:
                    msg = f"{type(e).__name__}: {str(e)}. Failed on deleting a relation. source:{source_obj}, target: {target_obj}"
                    log.error(f"{msg} {relationdata}")
                    failed_relations.append((relationdata, msg))
                    continue

            if len(failed_relations) > 0:
                return self._error(
                    422,
                    "Unprocessable Content",
                    "Failed on deleting relations",
                    failed_relations,
                )

        # Bunch of relations defined by source, target, relation name, or a combination of them
        else:
            relation = data.get("relation", None)
            source = data.get("source", None)
            target = data.get("target", None)

            source_obj = None
            if source:
                source_obj = plone_api_content_get(UID=source)
                if not source_obj:
                    source_obj = plone_api_content_get(path=source)
                if not source_obj:
                    msg = f"Failed on deleting relations. Source not found: {source}"
                    log.error(msg)
                    return self._error(422, "Unprocessable Content", msg)

            target_obj = None
            if target:
                target_obj = plone_api_content_get(UID=target)
                if not target_obj:
                    target_obj = plone_api_content_get(path=target)
                if not target_obj:
                    msg = f"Failed on deleting relations. Target not found: {target}"
                    log.error(msg)
                    return self._error(422, "Unprocessable Content", msg)

            try:
                api_relation_delete(
                    source=source_obj,
                    target=target_obj,
                    relationship=relation,
                )
            except Exception as e:
                msg = f"{type(e).__name__}: {str(e)}. Failed on deleting a relation. source:{source}, target: {target}, relation: {relation}"
                log.error(f"{msg} {data}")
                return self._error(422, type(e).__name__, msg)

        return self.reply_no_content()

    def _error(self, status, type, message, failed=[]):
        self.request.response.setStatus(status)
        return {"error": {"type": type, "message": message, "failed": failed}}
