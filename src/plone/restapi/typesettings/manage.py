"""Create, copy and remove content types, together with their settings."""

from plone.dexterity.fti import DexterityFTI
from plone.restapi.typesettings.interfaces import ITypeSettings
from Products.CMFCore.utils import getToolByName
from zope.component import getAdapters
from zope.component import queryMultiAdapter

ADD_VIEW_EXPR = "string:${folder_url}/++add++%s"
EMPTY_MODEL = (
    '<model xmlns="http://namespaces.plone.org/supermodel/schema">' "<schema /></model>"
)


def get_type_settings(fti, request):
    """Return the ``(name, adapter)`` pairs of a type's settings, in order."""
    return sorted(
        getAdapters((fti, request), ITypeSettings),
        key=lambda item: (item[1].order, item[0]),
    )


def count_items(context):
    """Return the number of catalogued items by portal type, for every type.

    The count includes items the current user cannot view.
    """
    catalog = getToolByName(context, "portal_catalog")
    index = catalog._catalog.getIndex("portal_type")
    return dict(index.uniqueValues(withLengths=True))


def create_type(types_tool, type_id, title, description=""):
    """Create a Dexterity container type with an empty schema.

    The defaults match the classic "Add Content Type" form.
    """
    fti = DexterityFTI(type_id)
    fti.manage_changeProperties(
        title=title,
        description=description or "",
        i18n_domain="plone",
        behaviors=("plone.dublincore", "plone.namefromtitle"),
        model_source=EMPTY_MODEL,
        klass="plone.dexterity.content.Container",
        filter_content_types=True,
        icon_expr="string:file-earmark-text",
    )
    types_tool._setObject(type_id, fti)
    return types_tool[type_id]


def copy_type(types_tool, source, type_id, title, description=None, request=None):
    """Copy a Dexterity type with its schema, behaviors, settings and workflow.

    Unlike copying the FTI properties only, this keeps the actions and method
    aliases of the source type.
    """
    source_id = source.getId()
    fti = source._getCopy(types_tool)
    fti._setId(type_id)
    # DexterityFTI only derives these from its ID when it is created.
    if fti.factory == source_id:
        fti._setPropValue("factory", type_id)
    if fti.add_view_expr == ADD_VIEW_EXPR % source_id:
        fti._setPropValue("add_view_expr", ADD_VIEW_EXPR % type_id)
    types_tool._setObject(type_id, fti)
    fti = types_tool[type_id]

    # Settings stored outside the FTI, like registry records.
    for name, settings in get_type_settings(source, request):
        target = queryMultiAdapter((fti, request), ITypeSettings, name=name)
        if target is not None:
            target.write(settings.read())
    properties = {"title": title}
    if description is not None:
        properties["description"] = description
    fti.manage_changeProperties(**properties)
    # Settings may have adjusted the behaviors. Keep the exact source order.
    if tuple(fti.behaviors) != tuple(source.behaviors):
        fti._updateProperty("behaviors", tuple(source.behaviors))

    repository = getToolByName(types_tool, "portal_repository")
    source_policies = repository.getPolicyMap().get(source_id, ())
    for policy in repository.listPolicies():
        if policy.getId() in source_policies:
            repository.addPolicyForContentType(type_id, policy.getId())
        else:
            repository.removePolicyFromContentType(type_id, policy.getId())

    workflow = getToolByName(types_tool, "portal_workflow")
    chain = dict(workflow.listChainOverrides()).get(source_id)
    workflow.setChainForPortalTypes((type_id,), chain)
    return fti


def remove_type(types_tool, type_id, request=None):
    """Remove a content type and what refers to it.

    This clears its settings, its workflow assignment and its use as an
    allowed type of other types, so a type created later with the same ID
    starts clean.
    """
    fti = types_tool[type_id]
    for name, settings in get_type_settings(fti, request):
        settings.remove()
    workflow = getToolByName(types_tool, "portal_workflow")
    workflow.setChainForPortalTypes((type_id,), None)
    for other in types_tool.listTypeInfo():
        allowed = tuple(other.allowed_content_types)
        if type_id in allowed and other.getId() != type_id:
            other.manage_changeProperties(
                allowed_content_types=tuple(t for t in allowed if t != type_id)
            )
    types_tool._delObject(type_id)
