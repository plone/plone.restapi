# -*- coding: utf-8 -*-
from Products.ATContentTypes.content.base import registerATCT
from Products.ATContentTypes.content.document import ATDocumentBase
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.Archetypes import atapi

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

    atapi.StringField('testReadonlyField', mode='r'),
    atapi.StringField('testURLField', validators=('isURL',)),
))


class ATTestDocument(ATDocumentBase):
    """A test type containing a set of standard Archetypes fields."""

    schema = ATTestDocumentSchema

    portal_type = 'TestDocument'


registerATCT(ATTestDocument, PROJECTNAME)
