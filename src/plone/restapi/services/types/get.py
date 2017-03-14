# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from plone.restapi.types.utils import get_jsonschema_for_portal_type
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from zope.schema.interfaces import IVocabularyFactory


class TypesGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(TypesGet, self).__init__(context, request)
        self.params = []

    def publishTraverse(self, request, name):
        # Treat any path segments after /@types as parameters
        self.params.append(name)
        return self

    @property
    def _get_record_name(self):
        if len(self.params) != 1:
            raise Exception(
                "Must supply exactly one parameter (dotted name of"
                "the record to be retrieved)")

        return self.params[0]

    def check_security(self):
        # Only expose type information to authenticated users
        portal_membership = getToolByName(self.context, 'portal_membership')
        if portal_membership.isAnonymousUser():
            raise Unauthorized

    def reply(self):
        self.check_security()

        if self.params and len(self.params) > 0:
            self.content_type = "application/json+schema"
            try:
                portal_type = self.params.pop()
                return get_jsonschema_for_portal_type(
                    portal_type,
                    self.context,
                    self.request
                )
            except KeyError:
                self.content_type = "application/json"
                self.request.response.setStatus(404)
                return {
                    'type': 'NotFound',
                    'message': 'Type "{}" could not be found.'.format(
                        portal_type
                    )
                }
        vocab_factory = getUtility(
            IVocabularyFactory,
            name="plone.app.vocabularies.ReallyUserFriendlyTypes"
        )

        # allowedContentTypes already checks for permissions
        allowed_types = [x.getId() for x in self.context.allowedContentTypes()]

        portal = getMultiAdapter((self.context, self.request),
                                 name='plone_portal_state').portal()
        portal_url = portal.absolute_url()

        # only addables if the content type is folderish
        can_add = IFolderish.providedBy(self.context)

        return [
            {
                '@id': '{}/@types/{}'.format(portal_url, x.token),
                'title': x.value,
                'addable': x.token in allowed_types if can_add else False,
            } for x in vocab_factory(self.context)
        ]
