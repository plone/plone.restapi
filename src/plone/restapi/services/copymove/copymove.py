# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.intid.interfaces import IIntIds


class BaseCopyMove(Service):
    """Base service for copy/move operations.
    """

    def __init__(self, context, request):
        super(BaseCopyMove, self).__init__(context, request)
        self.portal = getMultiAdapter((self.context, self.request),
                                      name='plone_portal_state').portal()
        self.portal_url = self.portal.absolute_url()
        self.catalog = getToolByName(self.context, 'portal_catalog')

    def get_object(self, key):
        """Get an object by intid, url, path or UID."""
        if isinstance(key, int):
            # Resolve by intid
            intids = queryUtility(IIntIds)
            return intids.queryObject(key)
        elif isinstance(key, basestring):
            if key.startswith(self.portal_url):
                # Resolve by URL
                return self.portal.restrictedTraverse(
                    key[len(self.portal_url) + 1:].encode('utf8'), None)
            elif key.startswith('/'):
                # Resolve by path
                return self.portal.restrictedTraverse(
                    key.encode('utf8').lstrip('/'), None)
            else:
                # Resolve by UID
                brain = self.catalog(UID=key)
                if brain:
                    return brain[0].getObject()

    def reply(self):
        data = json_body(self.request)

        source = data.get('source', None)

        if not source:
            raise BadRequest("Property 'source' is required")

        if not isinstance(source, list):
            source = [source]

        parents_ids = {}
        for item in source:
            obj = self.get_object(item)
            if obj is not None:
                parent = aq_parent(obj)
                if parent in parents_ids:
                    parents_ids[parent].append(obj.getId())
                else:
                    parents_ids[parent] = [obj.getId()]

        results = []
        for parent, ids in parents_ids.items():
            result = self.context.manage_pasteObjects(
                cb_copy_data=self.clipboard(parent, ids))
            for res in result:
                results.append({
                    'old': '{}/{}'.format(
                        parent.absolute_url(), res['id']),
                    'new': '{}/{}'.format(
                        self.context.absolute_url(), res['new_id']),
                    })
        return results

    def clipboard(self, parent, ids):
        """Get clipboard data"""
        raise NotImplementedError


class Copy(BaseCopyMove):
    """Copies existing content objects.
    """

    def clipboard(self, parent, ids):
        return parent.manage_copyObjects(ids=ids)


class Move(BaseCopyMove):
    """Moves existing content objects.
    """

    def clipboard(self, parent, ids):
        return parent.manage_cutObjects(ids=ids)
