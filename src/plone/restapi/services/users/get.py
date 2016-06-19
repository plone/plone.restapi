# -*- coding: utf-8 -*-
from plone import api
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zope.component import queryMultiAdapter
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
            result = []
            for user in api.user.get_users():
                serializer = queryMultiAdapter(
                    (user, self.request),
                    ISerializeToJson
                )
                result.append(serializer())
            return result
        # we retrieve the user on the user id not the username
        user = api.user.get(userid=self._get_user_id)
        serializer = queryMultiAdapter(
            (user, self.request),
            ISerializeToJson
        )
        return serializer()
