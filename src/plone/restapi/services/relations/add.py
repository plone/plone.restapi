from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.relations import plone_api_content_get
from plone.restapi.services.relations import api_relation_create
from zope.interface import alsoProvides
import plone.protect.interfaces
import logging


log = logging.getLogger(__name__)


class PostRelations(Service):
    """Create new relations."""

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        if not api_relation_create:
            raise NotImplementedError()

        data = json_body(self.request)

        failed_relations = []
        for relationdata in data["items"]:
            source_obj = plone_api_content_get(UID=relationdata["source"])
            if not source_obj:
                source_obj = plone_api_content_get(path=relationdata["source"])
            target_obj = plone_api_content_get(UID=relationdata["target"])
            if not target_obj:
                target_obj = plone_api_content_get(path=relationdata["target"])

            if not source_obj or not target_obj:
                msg = "Source and target not found." if not source_obj and not target_obj else "Source not found." if not source_obj else "Target not found."
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
            return {
                "type": "error",
                "failed": failed_relations,
            }

        return self.reply_no_content()
