# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.dexterity.interfaces import IDexterityContent
from plone.dexterity.fti import DexterityFTI
from plone.namedfile.field import NamedBlobFile as NamedBlobFileInterface
from plone.namedfile.file import NamedBlobFile

from plone.restapi.testing import \
    PLONE_RESTAPI_INTEGRATION_TESTING
from plone.restapi.interfaces import ISerializeToJson

from Products.CMFCore.utils import getToolByName

import json
import os


class IFileDocument(IDexterityContent):

    file = NamedBlobFileInterface(
        title=u"Please upload a file",
        required=False,
    )


class TestSerializeToJsonAdapter(unittest.TestCase):

    layer = PLONE_RESTAPI_INTEGRATION_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        fti = DexterityFTI('FileDocument')
        fti._updateProperty(
            'schema',
            'plone.restapi.tests.test_adapter_file.'
            'IFileDocument'
        )
        types_tool = getToolByName(self.portal, "portal_types")
        types_tool._setObject('FileDocument', fti)

    def test_file_adapter(self):
        self.portal.invokeFactory('FileDocument', 'filedoc1')
        file_file = os.path.join(os.path.dirname(__file__), u'file.pdf')
        self.portal.filedoc1.file = NamedBlobFile(
            data=open(file_file, 'r').read(),
            contentType='application/pdf',
            filename=u'file.pdf'
        )

        self.assertEqual(
            u'http://nohost/plone/filedoc1/file.pdf',
            json.loads(ISerializeToJson(self.portal.filedoc1)).get('file')
        )
