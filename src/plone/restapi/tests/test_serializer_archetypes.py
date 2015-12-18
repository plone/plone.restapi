# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.testing import PLONE_RESTAPI_AT_FUNCTIONAL_TESTING
from unittest2 import TestCase


class TestArchetypesSerializers(TestCase):
    layer = PLONE_RESTAPI_AT_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']

    def test_document(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        _ = self.portal.invokeFactory(
            id='document',
            type_name='Document',
            title='Document Title',
            text='<p>Some Text</p>')

        document = self.portal.get('document')
        self.maxDiff = None

        data_dict = ISerializeToJson(document)

        self.assertTrue('creation_date' in data_dict)
        self.assertTrue('modification_date' in data_dict)

        # Del dates to avoid date-checking
        del data_dict['creation_date']
        del data_dict['modification_date']

        self.assertDictEqual(
            {'@context': 'http://www.w3.org/ns/hydra/context.jsonld',
             '@id': 'http://localhost:55001/plone/document',
             '@type': 'Document',
             u'allowDiscussion': None,
             u'contributors': [],
             u'creators': [u'test_user_1_'],
             u'description': u'',
             u'effectiveDate': None,
             u'excludeFromNav': False,
             u'expirationDate': None,
             u'id': u'document',
             u'language': u'en',
             u'location': u'',
             'parent': {'@id': 'http://localhost:55001/plone',
                        'description': '',
                        'title': u'Plone site'},
             u'presentation': False,
             u'relatedItems': [],
             u'rights': u'',
             u'subject': [],
             u'tableContents': False,
             u'text': u'<p>Some Text</p>',
             u'title': u'Document Title'
             },
            data_dict)
