from Acquisition import aq_base
from DateTime import DateTime
from plone.app.content.interfaces import INameFromTitle
from plone.app.uuid.utils import uuidToObject
from plone.uuid.interfaces import IUUID
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import base_hasattr
from random import randint
from zExceptions import Unauthorized
from zope.component import getUtility
from zope.component.interfaces import IFactory
from zope.container.contained import notifyContainerModified
from zope.container.contained import ObjectAddedEvent
from zope.container.interfaces import INameChooser
from zope.event import notify


def create(container, type_, id_=None, title=None):
    """Create a new content item."""

    # Generate a temporary id if the id is not given
    if not id_:
        now = DateTime()
        new_id = "{}.{}.{}{:04d}".format(
            type_.lower().replace(" ", "_"),
            now.strftime("%Y-%m-%d"),
            str(now.millis())[7:],
            randint(0, 9999),
        )
    else:
        new_id = id_

    portal_types = getToolByName(container, "portal_types")
    type_info = portal_types.getTypeInfo(type_)

    if not type_info:
        raise Unauthorized(
            "Invalid '@type' parameter. No content type with the name '%s' found"
            % type_
        )

    # Check for add permission
    if not type_info.isConstructionAllowed(container):
        raise Unauthorized("Cannot create %s" % type_info.getId())

    # Check if allowed subobject type
    container_type_info = portal_types.getTypeInfo(container)
    if not container_type_info.allowType(type_):
        raise Unauthorized("Disallowed subobject type: %s" % type_)

    # Check for type constraints
    if type_ not in [fti.getId() for fti in container.allowedContentTypes()]:
        raise Unauthorized("Disallowed subobject type: %s" % type_)

    if type_info.product:
        # Oldstyle factory
        factory = type_info._getFactoryMethod(container, check_security=0)
        new_id = factory(new_id, title=title)
        obj = container._getOb(new_id)

    else:
        factory = getUtility(IFactory, type_info.factory)
        obj = factory(new_id, title=title)

    if base_hasattr(obj, "_setPortalTypeName"):
        obj._setPortalTypeName(type_info.getId())

    return obj


def add(container, obj, rename=True):
    """Add an object to a container."""
    old_id = getattr(aq_base(obj), "id", None)

    # Archetypes objects are already created in a container thus we just fire
    # the notification events and rename the object if necessary.
    if base_hasattr(obj, "_at_rename_after_creation"):
        notify(ObjectAddedEvent(obj, container, old_id))
        notifyContainerModified(container)
        if obj._at_rename_after_creation and rename:
            obj._renameAfterCreation(check_auto_id=True)
        return obj
    else:
        chooser = INameChooser(container)
        if rename:
            # INameFromTitle adaptable objects should not get a name
            # suggestion. NameChooser would prefer the given name instead of
            # the one provided by the INameFromTitle adapter.
            suggestion = None
            name_from_title = INameFromTitle(obj, None)
            if name_from_title is None:
                suggestion = obj.Title()
        else:
            suggestion = old_id
        id_ = chooser.chooseName(suggestion, obj)
        if not rename and id_ != old_id:
            raise ValueError(f"id is invalid or already used: {old_id}")
        obj.id = id_
        new_id = container._setObject(id_, obj)
        # _setObject triggers ObjectAddedEvent which can end up triggering a
        # content rule to move the item to a different container. In this case
        # look up the object by UUID.
        try:
            return container._getOb(new_id)
        except AttributeError:
            uuid = IUUID(obj)
            return uuidToObject(uuid)
