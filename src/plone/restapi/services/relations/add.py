from plone.app.uuid.utils import uuidToObject
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.relations import api_relation_create
from zope.interface import alsoProvides
import plone.protect.interfaces


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
            source_obj = uuidToObject(relationdata["source"])
            target_obj = uuidToObject(relationdata["target"])
            if not source_obj or not target_obj:
                failed_relations.append(relationdata)
                continue

            try:
                api_relation_create(
                    source=source_obj,
                    target=target_obj,
                    relationship=relationdata["relation"],
                )
            except Exception:
                failed_relations.append(relationdata)
                continue

        if len(failed_relations) > 0:
            return {
                "type": "error",
                "failed": failed_relations,
            }

        return self.reply_no_content()
