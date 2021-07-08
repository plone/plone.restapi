from plone import api


def slots_configuration(setup_context):
    setup_context.runImportStepFromProfile(
        "profile-plone.restapi.upgrades:0007",
        "rolemap",
        run_dependencies=False,
        purge_old=False,
    )
    setup_context.runImportStepFromProfile(
        "profile-plone.restapi.upgrades:0007",
        "plone.app.registry",
        run_dependencies=False,
        purge_old=False,
    )
    setup_context.runImportStepFromProfile(
        "profile-plone.restapi.upgrades:0007",
        "controlpanel",
        run_dependencies=False,
        purge_old=False,
    )
