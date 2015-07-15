# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.fti import DexterityFTI
from plone.namedfile.field import NamedBlobImage as NamedBlobImageInterface
from plone.namedfile.file import NamedBlobImage

from plone.restapi.testing import \
    PLONE_RESTAPI_INTEGRATION_TESTING
from plone.restapi.interfaces import ISerializeToJson

from Products.CMFCore.utils import getToolByName

import os


class IImageDocument(IDexterityContent):

    image = NamedBlobImageInterface(
        title=u"Please upload an image",
        required=False,
    )


class TestSerializeToJsonAdapter(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        fti = DexterityFTI('ImageDocument')
        fti._updateProperty(
            'schema',
            'plone.restapi.tests.test_adapter_image.'
            'IImageDocument'
        )
        types_tool = getToolByName(self.portal, "portal_types")
        types_tool._setObject('ImageDocument', fti)

    def test_image_adapter(self):
        self.portal.invokeFactory('ImageDocument', 'imagedoc1')
        image_file = os.path.join(os.path.dirname(__file__), u'image.png')
        self.portal.imagedoc1.image = NamedBlobImage(
            data=open(image_file, 'r').read(),
            contentType='image/png',
            filename=u'image.png'
        )
        self.portal.imagedoc1.image_caption = u'This is an image caption.'

        self.assertEqual(
            u'http://nohost/plone/imagedoc1/@@images/image',
            ISerializeToJson(self.portal.imagedoc1).get('image')
        )
