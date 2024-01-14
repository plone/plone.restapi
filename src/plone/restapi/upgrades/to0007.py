from plone import api

import logging


logger = logging.getLogger(__name__)


def site_administrator_permission(setup_context):
    """Give permission plone.restapi: Access Plone user information to
    Site Administrator"""
    api.portal.get().manage_permission(
        "plone.restapi: Access Plone user information",
        roles=["Manager", "Site Administrator"],
        acquire=1,
    )
    logger.info(
        "Give permission plone.restapi: Access Plone user information to Site Administrator"
    )
