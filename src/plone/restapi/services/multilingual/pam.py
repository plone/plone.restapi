# -*- coding: utf-8 -*-
from zope.interface import alsoProvides
from Products.CMFCore.utils import getToolByName
from plone.app.multilingual.interfaces import ITranslationManager
from plone.restapi.services import Service
from plone.restapi.deserializer import json_body
from Products.CMFPlone.interfaces import ILanguage

import plone.protect.interfaces


class TranslationInfo(Service):
    """ Get translation information
    """

    def reply(self):
        manager = ITranslationManager(self.context)
        info = {
            '@id': self.context.absolute_url(),
            'language': ILanguage(self.context).get_language(),
            'translations': []}
        for language, translation in manager.get_translations().items():
            if language != ILanguage(self.context).get_language():
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

        target_language = ILanguage(target).get_language()
        manager = ITranslationManager(self.context)
        current_translation = manager.get_translation(target_language)
        if current_translation is not None:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='Already translated into language {}'.format(
                    target_language)))

        manager.register_translation(target_language, target)
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
        manager = ITranslationManager(self.context)
        language = data.get('language', None)
        if language is None:
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='You need to provide the language to unlink'))

        if language not in manager.get_translations().keys():
            self.request.response.setStatus(400)
            return dict(error=dict(
                type='BadRequest',
                message='This objects is not translated into {}'.format(
                    language)))

        manager.remove_translation(language)
        self.request.response.setStatus(204)
        return {}
