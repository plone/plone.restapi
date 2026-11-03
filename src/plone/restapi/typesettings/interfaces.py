from plone.behavior.interfaces import IBehavior
from plone.restapi import _
from zope import schema
from zope.component import getUtilitiesFor
from zope.interface import Attribute
from zope.interface import Interface
from zope.interface import invariant
from zope.interface import provider
from zope.interface.exceptions import Invalid
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary


class ITypeSettings(Interface):
    """Settings of a content type, shown as one fieldset by @content-types.

    Register a named adapter for an FTI (``ITypeInformation``) and the request.
    The adapter name is the fieldset ID. Field names must be unique across all
    registered adapters.
    """

    title = Attribute("Fieldset title")
    order = Attribute("Fieldset sort order, lowest first")
    schema = Attribute("zope.schema interface declaring the settings")
    permission = Attribute(
        "Permission ID needed to read and change these settings, "
        "or None to only require the permission of the service"
    )

    def enabled():
        """Return whether to show these settings, e.g. only when the add-on
        that uses them is installed."""

    def read():
        """Return the stored values, keyed by field name, as Python values."""

    def validate(data):
        """Return a list of errors for an update, after field validation.

        ``data`` holds the converted values of the fields being changed.
        Errors are dicts with ``field`` and ``message``.
        """

    def write(data):
        """Store the converted values of the fields being changed."""

    def remove():
        """Delete what these settings store outside the FTI.

        Called before the content type is removed.
        """


def behavior_registrations():
    """Return every registered behavior once, by its name.

    Behaviors are registered under their short name and their interface
    identifier. Behaviors without a short name use the identifier.
    """
    registrations = {}
    for _name, registration in getUtilitiesFor(IBehavior):
        name = registration.name or registration.interface.__identifier__
        registrations.setdefault(name, registration)
    return registrations


# plone.behavior's ``Behaviors`` vocabulary has the behaviors' interface
# identifiers, but types list their behaviors by name.
BEHAVIORS_VOCABULARY = "plone.restapi.Behaviors"


@provider(IVocabularyFactory)
def behaviors_vocabulary(context):
    """Every registered behavior, by the name types list it with."""
    return SimpleVocabulary(
        [
            SimpleTerm(name, name, registration.title)
            for name, registration in sorted(behavior_registrations().items())
        ]
    )


def titled_vocabulary(*terms):
    return SimpleVocabulary([SimpleTerm(value, value, title) for value, title in terms])


class IGeneralSettings(Interface):
    title = schema.TextLine(title=_("Title"), min_length=1)
    description = schema.Text(
        title=_("Description"), required=False, default="", missing_value=""
    )


class IContentsSettings(Interface):
    global_allow = schema.Bool(
        title=_("Globally addable"),
        description=_("Allow adding content of this type in any folder"),
    )
    allowed_content_types_mode = schema.Choice(
        title=_("Allowed content types"),
        description=_(
            "Whether all types, only the selected types, or no types can be "
            "added inside content of this type"
        ),
        vocabulary=titled_vocabulary(
            ("all", _("All types")),
            ("selected", _("Selected types")),
            ("none", _("No types")),
        ),
    )
    allowed_content_types = schema.List(
        title=_("Selected types"),
        description=_("Kept while all types are allowed"),
        value_type=schema.Choice(vocabulary="plone.app.vocabularies.PortalTypes"),
        required=False,
        default=[],
        missing_value=[],
        unique=True,
    )

    @invariant
    def selected_types(data):
        mode, types = data.allowed_content_types_mode, data.allowed_content_types
        if mode == "selected" and not types:
            raise Invalid(_("Select at least one type"))
        if mode == "none" and types:
            raise Invalid(_("No types can be selected when none are allowed"))


class IVisibilitySettings(Interface):
    searchable = schema.Bool(title=_("Shown in search results"))
    default_page = schema.Bool(
        title=_("Usable as a default page"),
        description=_("Content of this type can be a folder's default page"),
    )
    in_navigation = schema.Bool(
        title=_("Shown in navigation"),
        description=_("Items of this type are listed in the site's navigation"),
    )


class ICommentsSettings(Interface):
    allow_discussion = schema.Bool(title=_("Allow comments"))


class IVersioningSettings(Interface):
    versioning = schema.Choice(
        title=_("Versioning"),
        description=_(
            "Manual versioning saves a version on request, automatic "
            "versioning also on every edit"
        ),
        vocabulary=titled_vocabulary(
            ("off", _("Off")),
            ("manual", _("Manual")),
            ("automatic", _("Automatic")),
        ),
    )


class IBehaviorsSettings(Interface):
    behaviors = schema.List(
        title=_("Behaviors"),
        description=_(
            "The complete list of the type's behaviors. Their order sets "
            "where their fields appear in the edit form."
        ),
        value_type=schema.Choice(vocabulary=BEHAVIORS_VOCABULARY),
        required=False,
        default=[],
        missing_value=[],
        unique=True,
    )


class ITypeCreation(Interface):
    """Body of a request creating a content type."""

    title = schema.TextLine(title=_("Title"), min_length=1)
    id = schema.TextLine(title=_("ID"), required=False, min_length=1)
    description = schema.Text(title=_("Description"), required=False)
    copy_from = schema.TextLine(title=_("Copy from"), required=False, min_length=1)
