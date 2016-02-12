# -*- coding: utf-8 -*-
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.Archetypes import atapi
from Products.CMFCore import permissions
from plone.app.folder.folder import ATFolder
from plone.app.folder.folder import ATFolderSchema

PROJECTNAME = 'plone.restapi.tests'

ATTestDocumentSchema = ATDocumentSchema.copy() + atapi.Schema((

    atapi.StringField('testStringField'),
    atapi.BooleanField('testBooleanField'),
    atapi.IntegerField('testIntegerField'),
    atapi.FloatField('testFloatField'),
    atapi.FixedPointField('testFixedPointField'),
    atapi.DateTimeField('testDateTimeField'),
    atapi.LinesField('testLinesField'),
    atapi.FileField('testFileField'),
    atapi.TextField('testTextField'),
    atapi.ImageField('testImageField'),
    atapi.ReferenceField('testReferenceField', relationship='testrelation'),
    atapi.ReferenceField('testMVReferenceField', relationship='testrelation',
                         multiValued=True),

    atapi.StringField('testRequiredField', required=True),
    atapi.StringField('testReadonlyField', mode='r'),
    atapi.StringField('testWriteonlyField', mode='w'),
    atapi.StringField('testReadPermissionField',
                      read_permission=permissions.ManagePortal),
    atapi.StringField('testWritePermissionField',
                      write_permission=permissions.ManagePortal),
    atapi.StringField('testURLField', validators=('isURL',)),
))


class ATTestDocument(ATDocumentBase):
    """A test type containing a set of standard Archetypes fields."""

    schema = ATTestDocumentSchema

    portal_type = 'ATTestDocument'


registerATCT(ATTestDocument, PROJECTNAME)


class ATTestFolder(ATFolder):
    """A test folderish Archetypes test type."""

    schema = ATFolderSchema

    portal_type = 'ATTestFolder'


registerATCT(ATTestFolder, PROJECTNAME)
