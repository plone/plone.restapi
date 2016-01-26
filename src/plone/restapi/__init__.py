# -*- coding: utf-8 -*-
from AccessControl import allow_module
allow_module('json')

import pkg_resources

try:
    pkg_resources.get_distribution('plone.app.testing')
except pkg_resources.DistributionNotFound:
    REGISTER_TEST_TYPES = False
else:
    REGISTER_TEST_TYPES = True


def initialize(context):
    if REGISTER_TEST_TYPES:
        from Products.Archetypes.ArchetypeTool import process_types, listTypes
        from Products.CMFCore import permissions
        from Products.CMFCore import utils
        from plone.restapi.tests.attypes import PROJECTNAME

        content_types, constructors, ftis = process_types(
            listTypes(PROJECTNAME), PROJECTNAME)

        utils.ContentInit(
            '%s Content' % PROJECTNAME,
            content_types=content_types,
            permission=permissions.AddPortalContent,
            extra_constructors=constructors,
            fti=ftis,
        ).initialize(context)
