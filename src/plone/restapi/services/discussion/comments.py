# -*- coding: utf-8 -*-
from plone.restapi.services import Service


class CommentsGet(Service):

    def reply(self):
        return {'comments': 'get'}
