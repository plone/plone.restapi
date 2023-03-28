from plone import api
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.relations import api_relation_delete
from zope.interface import alsoProvides
import plone.protect.interfaces
import logging


log = logging.getLogger(__name__)


def _delete_relation(source, target, relationship):
    # Cases could be handled by plone.api.relations.
    if source and relationship:
        api_relation_delete(
            source=source,
            relationship=relationship,
        )
    elif target and relationship:
        api_relation_delete(
            target=target,
            relationship=relationship,
        )
    elif source:
        api_relation_delete(
            source=source,
        )
    elif target:
        api_relation_delete(
            target=target,
        )
    elif relationship:
        api_relation_delete(
            relationship=relationship,
        )
    else:
        log.warning(
            f"Do not call _delete_relation without source object or target object or relationship. source:{source}, target: {target}, relationship {relationship}"
        )


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
                source_obj = api.content.get(UID=relationdata["source"])
                target_obj = api.content.get(UID=relationdata["target"])
                # Or maybe path provided?
                if not source_obj:
                    source_obj = api.content.get(path=relationdata["source"])
                if not target_obj:
                    target_obj = api.content.get(path=relationdata["target"])
                # Source or target not found by UID or path
                if not source_obj or not target_obj:
                    log.error(
                        f"Failed on deleting relation. Source or target not found. source:{relationdata['source']}, target: {relationdata['target']}"
                    )
                    failed_relations.append(relationdata)
                    continue

                try:
                    api_relation_delete(
                        source=source_obj,
                        target=target_obj,
                        relationship=relationdata["relation"],
                    )
                except Exception as e:
                    log.error(str(e))
                    log.error(
                        f"Failed on deleting relation. source:{source_obj}, target: {target_obj}"
                    )
                    failed_relations.append(relationdata)
                    continue

            if len(failed_relations) > 0:
                return {
                    "type": "error",
                    "failed": failed_relations,
                }

        # Bunch of relations defined by source, target, relation name, or a combination of them
        else:
            relation = data.get("relation", None)
            source = data.get("source", None)
            target = data.get("target", None)

            source_obj = None
            if source:
                source_obj = api.content.get(UID=relationdata["source"])
                if not source_obj:
                    source_obj = api.content.get(path=source)
                if not source_obj:
                    msg = f"Failed on deleting relations. Source not found: {source}"
                    log.error(msg)
                    return {
                        "type": "error",
                        "failed": msg,
                    }

            target_obj = None
            if target:
                target_obj = api.content.get(UID=relationdata["target"])
                if not target_obj:
                    target_obj = api.content.get(path=target)
                if not target_obj:
                    msg = f"Failed on deleting relations. Target not found: {target}"
                    log.error(msg)
                    return {
                        "type": "error",
                        "failed": msg,
                    }

            try:
                _delete_relation(
                    source=source_obj,
                    target=target_obj,
                    relationship=relation,
                )
            except Exception as e:
                log.error(str(e))
                msg = f"Failed on deleting relations. {str(e)} – source: {source}, target: {target}, relation: {relation}"
                log.error(msg)
                return {
                    "type": "error",
                    "failed": msg,
                }

        return self.reply_no_content()
