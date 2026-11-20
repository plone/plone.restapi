from plone.app.dexterity.behaviors.constrains import ACQUIRE
from plone.app.dexterity.behaviors.constrains import DISABLED
from plone.app.dexterity.behaviors.constrains import ENABLED
from plone.restapi.bbb import ISelectableConstrainTypes

MODE_TO_NAME = {
    ACQUIRE: "acquire",
    DISABLED: "disabled",
    ENABLED: "enabled",
}
NAME_TO_MODE = {name: mode for mode, name in MODE_TO_NAME.items()}


def get_constrain_adapter(context):
    return ISelectableConstrainTypes(context, None)


def _default_addable_types(adapter):
    return [
        {"id": fti.getId(), "title": fti.Title()}
        for fti in sorted(adapter.getDefaultAddableTypes(), key=lambda fti: fti.getId())
    ]


def serialize_constraints(context):
    adapter = get_constrain_adapter(context)
    result = {
        "@id": f"{context.absolute_url()}/@constraints",
        "addable_types": [],
        "can_edit": False,
        "configurable": adapter is not None,
        "immediately_addable_types": [],
        "locally_allowed_types": [],
        "mode": None,
    }
    if adapter is None:
        return result

    result["can_edit"] = bool(adapter.canSetConstrainTypes())
    result["mode"] = MODE_TO_NAME.get(adapter.getConstrainTypesMode())
    result["addable_types"] = _default_addable_types(adapter)
    result["locally_allowed_types"] = sorted(adapter.getLocallyAllowedTypes())
    result["immediately_addable_types"] = sorted(adapter.getImmediatelyAddableTypes())
    return result
