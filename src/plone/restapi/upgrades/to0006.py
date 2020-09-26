# -*- coding: utf-8 -*-
from plone import api
from zope.component import queryUtility
from plone.dexterity.interfaces import IDexterityFTI

import logging

logger = logging.getLogger(__name__)

DEPRECATED_NEW_BEHAVIOR_NAME = "plone.restapi.behaviors.IBlocks"
SHORT_NEW_NAME = "volto.blocks"


def rename_iface_to_name_in_blocks_behavior(setup_context):
    """Rename iface name to the short name in blocks"""
    pt = api.portal.get_tool("portal_types")

    for _type in pt.objectIds():
        fti = queryUtility(IDexterityFTI, name=_type)
        if fti and DEPRECATED_NEW_BEHAVIOR_NAME in fti.behaviors:
            new_fti = [
                currentbehavior
                for currentbehavior in fti.behaviors
                if currentbehavior != DEPRECATED_NEW_BEHAVIOR_NAME
            ]
            new_fti.append(SHORT_NEW_NAME)
            fti.behaviors = tuple(new_fti)
            logger.info("Migrated behavior of {} type".format(_type))
