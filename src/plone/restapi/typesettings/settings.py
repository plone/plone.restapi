"""Core content type settings."""

from plone.behavior.interfaces import IBehavior
from plone.dexterity.interfaces import IDexterityFTI
from plone.registry.interfaces import IRegistry
from plone.restapi import _
from plone.restapi.typesettings.interfaces import behavior_registrations
from plone.restapi.typesettings.interfaces import IBehaviorsSettings
from plone.restapi.typesettings.interfaces import ICommentsSettings
from plone.restapi.typesettings.interfaces import IContentsSettings
from plone.restapi.typesettings.interfaces import IGeneralSettings
from plone.restapi.typesettings.interfaces import ITypeSettings
from plone.restapi.typesettings.interfaces import IVersioningSettings
from plone.restapi.typesettings.interfaces import IVisibilitySettings
from Products.CMFCore.interfaces import ITypeInformation
from Products.CMFCore.utils import getToolByName
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryUtility
from zope.interface import implementer
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.schema import getFieldNames

# Repository policies for each versioning setting. Other policies are kept.
POLICIES = {
    "off": (),
    "manual": ("version_on_revert",),
    "automatic": ("at_edit_autoversion", "version_on_revert"),
}
VERSIONING_BEHAVIORS = (
    "plone.versioning",
    "plone.app.versioningbehavior.behaviors.IVersionable",
)
LOCKING_BEHAVIORS = (
    "plone.locking",
    "plone.app.lockingbehavior.behaviors.ILocking",
)


@adapter(ITypeInformation, IBrowserRequest)
@implementer(ITypeSettings)
class TypeSettings:
    """Base class for settings stored as properties of the FTI."""

    title = ""
    order = 100
    schema = None
    permission = None

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def read(self):
        return {
            name: getattr(self.context, name) for name in getFieldNames(self.schema)
        }

    def validate(self, data):
        return []

    def write(self, data):
        self.context.manage_changeProperties(**data)

    def remove(self):
        pass


class GeneralSettings(TypeSettings):
    title = _("General")
    order = 10
    schema = IGeneralSettings


class ContentsSettings(TypeSettings):
    title = _("Contents")
    order = 20
    schema = IContentsSettings

    def read(self):
        fti = self.context
        types = list(fti.allowed_content_types)
        if not fti.filter_content_types:
            mode = "all"
        elif types:
            mode = "selected"
        else:
            mode = "none"
        return {
            "global_allow": bool(fti.global_allow),
            "allowed_content_types_mode": mode,
            "allowed_content_types": types,
        }

    def write(self, data):
        data = dict(data)
        mode = data.pop("allowed_content_types_mode", None)
        if mode is not None:
            data["filter_content_types"] = mode != "all"
        if "allowed_content_types" in data:
            data["allowed_content_types"] = tuple(data["allowed_content_types"] or ())
        super().write(data)


class VisibilitySettings(TypeSettings):
    title = _("Visibility")
    order = 30
    schema = IVisibilitySettings
    # Field name, registry record, and whether the record lists excluded types
    RECORDS = (
        ("searchable", "plone.types_not_searched", True),
        ("default_page", "plone.default_page_types", False),
    )

    def read(self):
        registry = getUtility(IRegistry)
        name = self.context.getId()
        return {
            field: (name in registry[record]) != excluded
            for field, record, excluded in self.RECORDS
        }

    def write(self, data):
        registry = getUtility(IRegistry)
        name = self.context.getId()
        for field, record, excluded in self.RECORDS:
            if field not in data:
                continue
            values = [value for value in registry[record] if value != name]
            if data[field] != excluded:
                values.append(name)
            registry[record] = type(registry[record])(values)

    def remove(self):
        registry = getUtility(IRegistry)
        name = self.context.getId()
        for field, record, excluded in self.RECORDS:
            values = registry[record]
            if name in values:
                registry[record] = type(values)(v for v in values if v != name)


class CommentsSettings(TypeSettings):
    title = _("Comments")
    order = 40
    schema = ICommentsSettings

    def read(self):
        return {"allow_discussion": bool(self.context.allow_discussion)}


class VersioningSettings(TypeSettings):
    title = _("Versioning")
    order = 50
    schema = IVersioningSettings

    @property
    def repository(self):
        return getToolByName(self.context, "portal_repository")

    def read(self):
        name = self.context.getId()
        if name not in self.repository.getVersionableContentTypes():
            return {"versioning": "off"}
        policies = self.repository.getPolicyMap().get(name, ())
        if "at_edit_autoversion" in policies:
            return {"versioning": "automatic"}
        return {"versioning": "manual"}

    def write(self, data):
        if "versioning" not in data:
            return
        name = self.context.getId()
        enabled = POLICIES[data["versioning"]]
        repository = self.repository
        types = [t for t in repository.getVersionableContentTypes() if t != name]
        if enabled:
            types.append(name)
        repository.setVersionableContentTypes(types)
        available = {policy.getId() for policy in repository.listPolicies()}
        for policy_id in POLICIES["automatic"]:
            if policy_id not in available:
                continue
            if policy_id in enabled:
                repository.addPolicyForContentType(name, policy_id)
            else:
                repository.removePolicyFromContentType(name, policy_id)
        if IDexterityFTI.providedBy(self.context):
            self.write_behaviors(bool(enabled))

    def write_behaviors(self, enabled):
        """Versioning needs its behavior, and locking to edit safely."""
        behaviors = list(self.context.behaviors)
        if enabled:
            for names in (VERSIONING_BEHAVIORS, LOCKING_BEHAVIORS):
                if not set(names) & set(behaviors):
                    behaviors.append(names[0])
        else:
            # Locking stays, as it is useful without versioning.
            behaviors = [b for b in behaviors if b not in VERSIONING_BEHAVIORS]
        if tuple(behaviors) != tuple(self.context.behaviors):
            self.context._updateProperty("behaviors", tuple(behaviors))

    def remove(self):
        name = self.context.getId()
        repository = self.repository
        types = repository.getVersionableContentTypes()
        if name in types:
            repository.setVersionableContentTypes([t for t in types if t != name])
        for policy_id in tuple(repository.getPolicyMap().get(name, ())):
            repository.removePolicyFromContentType(name, policy_id)


def behavior_name(stored):
    """Return the name a stored behavior is listed under, or ``None``.

    FTIs can store a behavior by its interface identifier or a former dotted
    name.
    """
    registration = queryUtility(IBehavior, name=stored)
    if registration is None:
        for candidate in behavior_registrations().values():
            if stored in candidate.former_dotted_names:
                registration = candidate
                break
    if registration is None:
        return None
    return registration.name or registration.interface.__identifier__


@adapter(IDexterityFTI, IBrowserRequest)
class BehaviorsSettings(TypeSettings):
    """The ordered behaviors of a Dexterity type."""

    title = _("Behaviors")
    # Before versioning, which is written after it: in a PATCH that changes
    # both, the versioning setting decides about the versioning behavior.
    order = 45
    schema = IBehaviorsSettings

    def read(self):
        names = [behavior_name(stored) for stored in self.context.behaviors]
        return {"behaviors": [name for name in names if name]}

    def write(self, data):
        if "behaviors" not in data:
            return
        # Behaviors that aren't registered aren't listed, so a new list
        # doesn't remove them: they come back if their add-on does.
        unknown = [
            stored for stored in self.context.behaviors if not behavior_name(stored)
        ]
        behaviors = tuple(data["behaviors"] or ()) + tuple(unknown)
        if behaviors != tuple(self.context.behaviors):
            self.context.manage_changeProperties(behaviors=behaviors)
