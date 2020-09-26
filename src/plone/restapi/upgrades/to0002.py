# -*- coding: utf-8 -*-


def assign_use_api_permission(setup_context):
    """Assign the 'plone.restapi: Use REST API' permission to Anonymous."""
    setup_context.runImportStepFromProfile(
        "profile-plone.restapi.upgrades:0002",
        "rolemap",
        run_dependencies=False,
        purge_old=False,
    )
