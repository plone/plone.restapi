# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.services import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse


class UsersGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(UsersGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_user_id(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (user id)")
        return self.params[0]

    def reply(self):
        if len(self.params) == 0:
            return [
                {
                    'id': user.id,
                    'email': user.getProperty('email'),
                    'username': user.getUserName(),
                    'fullname': user.getProperty('fullname'),
                    'home_page': user.getProperty('home_page'),
                    'description': user.getProperty('description'),
                    'location': user.getProperty('location')
                } for user in api.user.get_users()
            ]
        # we retrieve the user on the user id not the username
        user = api.user.get(userid=self._get_user_id)
        return {
            'id': user.id,
            'email': user.getProperty('email'),
            'username': user.getUserName(),
            'fullname': user.getProperty('fullname'),
            'home_page': user.getProperty('home_page'),
            'description': user.getProperty('description'),
            'location': user.getProperty('location')
        }
