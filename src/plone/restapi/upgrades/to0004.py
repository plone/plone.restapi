def assign_get_users_permission(setup_context):
    """Assign the 'plone.restapi: Access Plone user information' permission
    to Managers by default.
    """
    setup_context.runImportStepFromProfile(
        "profile-plone.restapi.upgrades:0004",
        "rolemap",
        run_dependencies=False,
        purge_old=False,
    )
