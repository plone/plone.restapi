# -*- coding: utf-8 -*-
from Acquisition import aq_parent
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.security import checkPermission

import plone
import six


class BaseCopyMove(Service):
    """Base service for copy/move operations."""

    def __init__(self, context, request):
        super(BaseCopyMove, self).__init__(context, request)
        self.portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        self.portal_url = self.portal.absolute_url()
        self.catalog = getToolByName(self.context, "portal_catalog")

    def get_object(self, key):
        """Get an object by url, path or UID."""
        if key.startswith(self.portal_url):
            # Resolve by URL
            key = key[len(self.portal_url) + 1 :]
            if six.PY2:
                key = key.encode("utf8")
            return self.portal.restrictedTraverse(key, None)
        elif key.startswith("/"):
            if six.PY2:
                key = key.encode("utf8")
            # Resolve by path
            return self.portal.restrictedTraverse(key.lstrip("/"), None)
        else:
            # Resolve by UID
            brain = self.catalog(UID=key)
            if brain:
                return brain[0].getObject()

    def reply(self):
        # return 401/403 Forbidden if the user has no permission
        if not checkPermission("cmf.AddPortalContent", self.context):
            pm = getToolByName(self.context, "portal_membership")
            if bool(pm.isAnonymousUser()):
                self.request.response.setStatus(401)
            else:
                self.request.response.setStatus(403)
            return

        data = json_body(self.request)

        source = data.get("source", None)

        if not source:
            raise BadRequest("Property 'source' is required")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        if not isinstance(source, list):
            source = [source]

        parents_ids = {}
        for item in source:
            obj = self.get_object(item)
            if obj is not None:
                if self.is_moving:
                    # To be able to safely move the object, the user requires
                    # permissions on the parent
                    if not checkPermission(
                        "zope2.DeleteObjects", obj
                    ) and not checkPermission("zope2.DeleteObjects", aq_parent(obj)):
                        self.request.response.setStatus(403)
                        return
                parent = aq_parent(obj)
                if parent in parents_ids:
                    parents_ids[parent].append(obj.getId())
                else:
                    parents_ids[parent] = [obj.getId()]

        results = []
        for parent, ids in parents_ids.items():
            result = self.context.manage_pasteObjects(
                cb_copy_data=self.clipboard(parent, ids)
            )
            for res in result:
                results.append(
                    {
                        "source": "{}/{}".format(parent.absolute_url(), res["id"]),
                        "target": "{}/{}".format(
                            self.context.absolute_url(), res["new_id"]
                        ),
                    }
                )
        return results

    def clipboard(self, parent, ids):
        """Get clipboard data"""
        raise NotImplementedError


class Copy(BaseCopyMove):
    """Copies existing content objects."""

    is_moving = False

    def clipboard(self, parent, ids):
        return parent.manage_copyObjects(ids=ids)


class Move(BaseCopyMove):
    """Moves existing content objects."""

    is_moving = True

    def clipboard(self, parent, ids):
        return parent.manage_cutObjects(ids=ids)
