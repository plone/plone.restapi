# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.app.testing import TEST_USER_ID
from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.registry.record import Record
from plone.restapi.testing import PLONE_RESTAPI_DX_FUNCTIONAL_TESTING
from plone.restapi.testing import RelativeSession
from zope.component import getUtility

import transaction
import unittest


class TestRegistry(unittest.TestCase):

    layer = PLONE_RESTAPI_DX_FUNCTIONAL_TESTING

    def setUp(self):
        self.app = self.layer['app']
        self.portal = self.layer['portal']
        self.portal_url = self.portal.absolute_url()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        self.api_session = RelativeSession(self.portal_url)
        self.api_session.headers.update({'Accept': 'application/json'})
        self.api_session.auth = (SITE_OWNER_NAME, SITE_OWNER_PASSWORD)

        registry = getUtility(IRegistry)
        record = Record(field.TextLine(title=u"Foo Bar"), u"Lorem Ipsum")
        registry.records['foo.bar'] = record
        transaction.commit()

    def test_get_registry_record(self):

        transaction.commit()

        response = self.api_session.get('/registry_/foo.bar')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Lorem Ipsum')

    def test_update_registry_record(self):
        registry = getUtility(IRegistry)
        payload = {'foo.bar': 'Lorem Ipsum'}
        response = self.api_session.put('/registry_', json=payload)

        self.assertEqual(response.status_code, 204)
        self.assertEqual(registry['foo.bar'], 'Lorem Ipsum')
