# -*- coding: utf-8 -*-
from plone import api
from zope.component import queryUtility
from plone.dexterity.interfaces import IDexterityFTI

import logging

logger = logging.getLogger(__name__)

CUSTOM_BLOCKS_BEHAVIOR = "volto.blocks.custom"
AUTO_DISABLE_BEHAVIORS = ("volto.blocks", "plone.restapi.behaviors.IBlocks")


def fix_custom_volto_blocks_behavior(setup_context):
    """Add missing volto.blocks.custom marker interface"""
    pt = api.portal.get_tool("portal_types")

    for _type in pt.objectIds():
        fti = queryUtility(IDexterityFTI, name=_type)
        if CUSTOM_BLOCKS_BEHAVIOR in fti.behaviors:
            # Already fixed
            continue

        model_source = fti.model_source
        if 'name="blocks_layout"' in model_source or 'name="blocks"' in model_source:
            new_behaviors = [
                b for b in fti.behaviors if b not in AUTO_DISABLE_BEHAVIORS
            ]
            new_behaviors.append(CUSTOM_BLOCKS_BEHAVIOR)
            fti.behaviors = tuple(new_behaviors)
            logger.info("Fixed volto.blocks.custom behavior of {} type".format(_type))
