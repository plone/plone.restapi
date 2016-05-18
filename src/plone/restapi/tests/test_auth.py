# -*- coding: utf-8 -*-
from ZPublisher.pubevents import PubStart
from plone.app.testing import SITE_OWNER_NAME
from plone.app.testing import SITE_OWNER_PASSWORD
from plone.restapi.testing import PLONE_RESTAPI_DX_INTEGRATION_TESTING
from unittest2 import TestCase
from zope.event import notify


class TestLogin(TestCase):

    layer = PLONE_RESTAPI_DX_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

    def traverse(self, path='/plone/login', accept='application/json',
                 method='POST'):
        request = self.layer['request']
        request.environ['PATH_INFO'] = path
        request.environ['PATH_TRANSLATED'] = path
        request.environ['HTTP_ACCEPT'] = accept
        request.environ['REQUEST_METHOD'] = method
        notify(PubStart(request))
        return request.traverse(path)

    def test_login_without_pas_plugin_fails(self):
        self.portal.acl_users._delOb('jwt_auth')
        service = self.traverse()
        res = service.render()
        self.assertIn('error', res)
        self.assertNotIn('token', res)

    def test_login_without_credentials_fails(self):
        service = self.traverse()
        res = service.render()
        self.assertIn('error', res)
        self.assertNotIn('token', res)

    def test_login_with_invalid_credentials_fails(self):
        self.request['BODY'] = '{"login": "admin", "password": "admin"}'
        service = self.traverse()
        res = service.render()
        self.assertIn('error', res)
        self.assertNotIn('token', res)

    def test_successful_login_returns_token(self):
        self.request['BODY'] = '{"login": "%s", "password": "%s"}' % (
            SITE_OWNER_NAME, SITE_OWNER_PASSWORD)
        service = self.traverse()
        res = service.render()
        self.assertIn('token', res)
