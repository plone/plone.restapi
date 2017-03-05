# -*- coding: utf-8 -*-
from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName
from plone.restapi.services import Service
from plone.restapi.deserializer import json_body

import plone.protect.interfaces


class TranslationInfo(Service):
    """ Get translation information
    """

    def reply(self):
        info = {
            '@id': self.context.absolute_url(),
            'language': self.context.Language(),
            'translations': []}
        for language, translation in self.context.getTranslations(review_state=False).items():
            if language != self.context.Language():
                info['translations'].append({
                    '@id': translation.absolute_url(),
                    'language': language,
                    })

        return info


class LinkTranslations(Service):
    """ Link two content objects as translations of each other
    """

    def reply(self):
        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        id_ = data.get('id', None)
        if id_ is None:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Missing content id to link to'))

        target = self._traverse(id_)
        if target is None:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Content does not exist'))

        target_language = target.Language()
        if target.hasTranslation(target_language):
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Already translated into language {}'.format(
                    target_language)))

        self.context.addTranslationReference(target)
        self.request.response.setStatus(201)
        self.request.response.setHeader(
            'Location', self.context.absolute_url())
        return {}

    def _traverse(self, url):
        purl = getToolByName(self.context, 'portal_url')
        portal = purl.getPortalObject()
        portal_url = portal.absolute_url()
        if url.startswith(portal_url):
            content_path = url[len(portal_url)+1:]
            content_path = content_path.split('/')
            content_item = portal.restrictedTraverse(content_path)
            return content_item

        return None


class UnlinkTranslations(Service):
    """ Unlink the translations for a content object
    """

    def reply(self):
        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        data = json_body(self.request)
        language = data.get('language', None)
        if language is None:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='You need to provide the language to unlink'))

        if not self.context.hasTranslation(language):
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='This object is not translated into {}'.format(
                    language)))

        self.context.removeTranslation(language)
        self.request.response.setStatus(204)
        return {}
