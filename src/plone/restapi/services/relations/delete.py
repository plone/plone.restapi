from plone import api
from plone.app.uuid.utils import uuidToObject
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
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

        # TODO delete by relation name, source or target

        # Delete all relations of the type `comprisesComponentPart` from any source to any target:

        # ```
        # DELETE /plone/@relations?relation=comprisesComponentPart
        # ```

        # Delete all relations outgoing from a certain item:

        # ```
        # DELETE /plone/@relations?source=uuid1
        # ```

        # Delete all relations to a certain item:

        # ```
        # DELETE /plone/@relations?target=uuid1
        # ```

        # Or delete the relations of type `comprisesComponentPart` to a target object:

        # ```
        # DELETE /plone/@relations?relation=comprisesComponentPart&target=uuid1
        # ```

        failed_relations = []
        # List of single relations
        if data.get("items", None):
            for relationdata in data["items"]:
                # UIDs provided?
                source_obj = uuidToObject(relationdata["source"])
                target_obj = uuidToObject(relationdata["target"])
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
                        f"Failed on deleting relation. source:{source}, target: {target}"
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
            # TODO delete by …
            pass

        return self.reply_no_content()
