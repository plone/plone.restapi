from plone import api
from plone.restapi.services import Service
from collections import Counter
from plone.dexterity.content import get_assignable


class BlockTypesGet(Service):
    def reply(self):
        catalog = api.portal.get_tool(name="portal_catalog")
        request_body = self.request.form
        result = {}

        if request_body.get("blocktypes") != "":
            blocktypes = request_body.get("blocktypes").split(",")

            for blocktype in blocktypes:
                brains = catalog.searchResults(block_types=blocktype)
                result[blocktype] = Counter()

                for brain in brains:
                    obj = brain.getObject()
                    assignable = get_assignable(obj)

                    hasBlocksBehavior = bool(
                        {
                            behavior
                            for behavior in assignable.enumerateBehaviors()
                            if behavior.name == "volto.blocks"
                        }
                    )

                    if hasBlocksBehavior:
                        url = brain.getURL()  # or brain.getPath()

                        for block in obj.blocks.values():
                            if block["@type"] == blocktype:
                                result[blocktype].update({url: 1})

        return result
