from AccessControl import getSecurityManager
from Acquisition import aq_base
from Acquisition.interfaces import IAcquirer
from plone.app.multilingual.interfaces import IPloneAppMultilingualInstalled
from plone.app.multilingual.interfaces import ITranslationManager
from plone.restapi.deserializer import json_body
from plone.restapi.exceptions import DeserializationError
from plone.restapi.interfaces import IDeserializeFromJson
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.content.utils import add
from plone.restapi.services.content.utils import create
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_hasattr
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import queryMultiAdapter
from zope.event import notify
from zope.interface import alsoProvides
from zope.lifecycleevent import ObjectCreatedEvent
from zope.component import getMultiAdapter

import plone.protect.interfaces


class FolderPost(Service):
    """Creates a new content object."""

    def reply(self):
        data = json_body(self.request)

        type_ = data.get("@type", None)
        id_ = data.get("id", None)
        title = data.get("title", None)
        translation_of = data.get("translation_of", None)
        language = data.get("language", None)
        uid = data.get("UID", None)

        if not type_:
            raise BadRequest("Property '@type' is required")

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        sm = getSecurityManager()
        # ManagePortal is required to set the uid of an object during creation
        if uid and not sm.checkPermission(ManagePortal, self.context):
            self.request.response.setStatus(403)
            msg = "Setting UID of an object requires Manage Portal permission"
            return dict(error=dict(type="Forbidden", message=msg))

        try:
            obj = create(self.context, type_, id_=id_, title=title)
        except Unauthorized as exc:
            self.request.response.setStatus(403)
            return dict(error=dict(type="Forbidden", message=str(exc)))
        except BadRequest as exc:
            self.request.response.setStatus(400)
            return dict(error=dict(type="Bad Request", message=str(exc)))

        # Acquisition wrap temporarily to satisfy things like vocabularies
        # depending on tools
        temporarily_wrapped = False
        if IAcquirer.providedBy(obj) and not safe_hasattr(obj, "aq_base"):
            obj = obj.__of__(self.context)
            temporarily_wrapped = True

        # Update fields
        deserializer = queryMultiAdapter((obj, self.request), IDeserializeFromJson)
        if deserializer is None:
            self.request.response.setStatus(501)
            return dict(
                error=dict(message=f"Cannot deserialize type {obj.portal_type}")
            )

        try:
            deserializer(validate_all=True, create=True)
        except DeserializationError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="DeserializationError", message=str(e)))

        if temporarily_wrapped:
            obj = aq_base(obj)

        if uid:
            setattr(obj, "_plone.uuid", uid)

        if not getattr(deserializer, "notifies_create", False):
            notify(ObjectCreatedEvent(obj))

        try:
            obj = add(self.context, obj, rename=not bool(id_))
        except ValueError as e:
            self.request.response.setStatus(400)
            return dict(error=dict(type="ValueError", message=str(e)))

        # Link translation given the translation_of property
        if (
            IPloneAppMultilingualInstalled.providedBy(self.request)
            and translation_of
            and language
        ):
            source = self.get_object(translation_of)
            if source:
                manager = ITranslationManager(source)
                manager.register_translation(language, obj)

        self.request.response.setStatus(201)
        self.request.response.setHeader("Location", obj.absolute_url())

        serializer = queryMultiAdapter((obj, self.request), ISerializeToJson)

        serialized_obj = serializer()

        # HypermediaBatch can't determine the correct canonical URL for
        # objects that have just been created via POST - so we make sure
        # to set it here
        serialized_obj["@id"] = obj.absolute_url()

        return serialized_obj

    def get_object(self, key):
        portal = getMultiAdapter(
            (self.context, self.request), name="plone_portal_state"
        ).portal()
        catalog = getToolByName(self.context, "portal_catalog")

        if key.startswith(portal.absolute_url()):
            # Resolve by URL
            key = key[len(portal.absolute_url()) + 1 :]
            return portal.restrictedTraverse(key, None)
        elif key.startswith("/"):
            # Resolve by path
            return portal.restrictedTraverse(key.lstrip("/"), None)
        else:
            # Resolve by UID
            brain = catalog(UID=key)
            if brain:
                return brain[0].getObject()
