# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound
from zope.component import queryMultiAdapter
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


@implementer(IPublishTraverse)
class TypesDelete(Service):
    """Deletes a type.
    """

    def __init__(self, context, request):
        super(TypesDelete, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Consume any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _get_type_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (type id)")
        return self.params[0]

    def _get_type(self, type_id):
        ttool = getToolByName(self.context, 'portal_types')
        return ttool.get(type_id)

    def reply(self):
        context = queryMultiAdapter((self.context, self.request), name='dexterity-types')
        edit = queryMultiAdapter((context, self.request), name='edit')

        tid = self._get_type_id
        fti = self._get_type(tid)
        if not fti:
            raise NotFound("Trying to delete a non-existing type.")

        edit.form_instance.remove((tid,))
        return self.reply_no_content()
