# -*- coding: utf-8 -*-
from datetime import datetime
from pkg_resources import resource_filename
from plone.app.contenttypes.behaviors.richtext import IRichText
from plone.app.dexterity.behaviors.metadata import ICategorization
from plone.dexterity.utils import createContentInContainer
from plone.dexterity.utils import iterSchemata
from plone.namedfile.file import NamedBlobFile
from plone.namedfile.file import NamedBlobImage
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from unittest2 import TestCase
from zope.component import getMultiAdapter
from zope.interface.verify import verifyClass
from zope.schema import getFields
import json


class TestDexterityFieldSerializing(TestCase):
    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def test_boolean(self):
        folder = createContentInContainer(self.portal, u'Folder',
                                          exclude_from_nav=True)
        value = self.serialize(folder, u'exclude_from_nav')
        self.assertEquals(True, value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_textline(self):
        folder = createContentInContainer(self.portal, u'Folder',
                                          title=u'My Folder')
        value = self.serialize(folder, u'title')
        self.assertEquals(u'My Folder', value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_choice(self):
        folder = createContentInContainer(self.portal, u'Folder',
                                          language=u'lo')
        value = self.serialize(folder, u'language')
        self.assertEquals(u'lo', value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_date(self):
        folder = createContentInContainer(
            self.portal, u'Folder',
            effective_date=datetime(2017, 10, 22, 19, 45, 1))
        value = self.serialize(folder, u'effective')
        self.assertEquals(u'2017-10-22T19:45:01', value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_richtext(self):
        document = createContentInContainer(
            self.portal, u'Document',
            text=IRichText['text'].fromUnicode(u'<p>Some Text</p>'))
        value = self.serialize(document, u'text')
        self.assertEquals(u'<p>Some Text</p>', value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_tuple(self):
        document = createContentInContainer(self.portal, u'Document')
        ICategorization(document).subjects = (u'Foo', u'Bar')
        value = self.serialize(document, u'subjects')
        self.assertEquals([u'Foo', u'Bar'], value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_named_image(self):
        image_asset_path = resource_filename('plone.restapi.tests',
                                             'image.png')
        with open(image_asset_path, 'rb') as image_asset:
            image_blob = NamedBlobImage(
                data=image_asset.read(),
                contentType='image/png',
                filename=u'image.png')

        image = createContentInContainer(self.portal, u'Image',
                                         id=u'the-image')
        self.get_field_by_name(image, 'image').set(image, image_blob)

        value = self.serialize(image, u'image')

        obj_url = image.absolute_url()
        self.assertDictEqual(
            {u'original': u'{}/@@images/image'.format(obj_url),
             u'mini': u'{}/@@images/image/mini'.format(obj_url),
             u'thumb': u'{}/@@images/image/thumb'.format(obj_url),
             u'large': u'{}/@@images/image/large'.format(obj_url),
             u'listing': u'{}/@@images/image/listing'.format(obj_url),
             u'tile': u'{}/@@images/image/tile'.format(obj_url),
             u'preview': u'{}/@@images/image/preview'.format(obj_url),
             u'icon': u'{}/@@images/image/icon'.format(obj_url)},
            value)
        self.assertEquals(value, json.loads(json.dumps(value)))

    def test_named_file(self):
        file_asset_path = resource_filename('plone.restapi.tests', 'file.pdf')
        with open(file_asset_path, 'rb') as file_asset:
            file_blob = NamedBlobFile(
                data=file_asset.read(),
                contentType='application/pdf',
                filename=u'file.pdf')

        file = createContentInContainer(self.portal, u'File',
                                        id=u'the-file')
        self.get_field_by_name(file, 'file').set(file, file_blob)

        value = self.serialize(file, u'file')
        portal_url = self.portal.portal_url()
        self.assertEquals(portal_url + '/the-file/@@download/file', value)
        self.assertEquals(portal_url + '/the-file/@@download/file',
                          json.loads(json.dumps(value)))

    def serialize(self, context, fieldname):
        field = self.get_field_by_name(context, fieldname)
        serializer = getMultiAdapter((field, context, self.request),
                                     IFieldSerializer)
        return serializer()

    def get_field_by_name(self, context, fieldname):
        for schemata in iterSchemata(context):
            fields = getFields(schemata)
            if fieldname in fields:
                return fields[fieldname]

        raise AttributeError(u'Field "{}" not found for "{}"'.format(
            fieldname, context))


class TestDexterityFieldSerializers(TestCase):

    def default_field_serializer(self):
        verifyClass(IFieldSerializer, DefaultFieldSerializer)
