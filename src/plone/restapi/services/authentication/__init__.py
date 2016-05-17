# -*- coding: utf-8 -*-
from plone.rest import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
import jwt
import time


class Login(Service):

    # should be in keyring...
    secret = 'foobar'

    implements(IPublishTraverse)

    def render(self):
        data = {
            'algorithm': 'HS256',
            'type': 'JWT',
            'username': 'admin',
            'fullname': 'Foo bar',
            'expires': time.time() + (60 * 60 * 12)  # 12 hour length?
        }
        encoded = jwt.encode(data, self.secret, algorithm='HS256')
        return {
            'success': True,
            'jwt': data,
            'signature': encoded
        }


class Logout(Service):
    implements(IPublishTraverse)

    def render(self):
        # doing nothing right now
        return {
            'success': True
        }
