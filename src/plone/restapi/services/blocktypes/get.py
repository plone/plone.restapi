from plone import api
from plone.restapi.services import Service
from collections import Counter
from plone.restapi.behaviors import IBlocks
from plone.restapi.blocks import visit_blocks


class BlockTypesGet(Service):
    def reply(self):
        catalog = api.portal.get_tool(name="portal_catalog")
        request_body = self.request.form
        result = {}

        if request_body.get("blocktypes") != "":
            blocktypes = request_body.get("blocktypes").split(",")

            for blocktype in blocktypes:
                brains = catalog(object_provides=IBlocks.__identifier__)
                result[blocktype] = Counter()

                for brain in brains:
                    obj = brain.getObject()
                    url = brain.getPath() # or .getURL()
                    title = obj.title
                    result[blocktype][title] = Counter()

                    for block in visit_blocks(obj, obj.blocks):
                        if block["@type"] == blocktype:
                            result[blocktype][title].update({url: 1})

        return result
