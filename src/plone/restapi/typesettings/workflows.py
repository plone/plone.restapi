"""Plan and apply changes of the workflow of content types."""

from plone.app.workflow.remap import remap_workflow
from Products.CMFCore.utils import getToolByName

DEFAULT_CHAIN = "(Default)"
# The state of items without a workflow.
NO_STATE = ""
# Who can see items in a state, from the fewest to the most people.
VISIBILITY_RANKS = {"unknown": 0, "restricted": 0, "members": 1, "anyone": 2}


def visibility(state):
    """Summarize who can see items in a workflow state.

    DCWorkflow stores the roles of an acquired permission as a list, and of
    the others as a tuple.
    """
    roles = (state.permission_roles or {}).get("View")
    if roles is None:
        return "unknown"
    if "Anonymous" in roles:
        return "anyone"
    if isinstance(roles, list):
        return "unknown"
    if "Authenticated" in roles or "Member" in roles:
        return "members"
    return "restricted"


def get_workflow(context, chain):
    """Return the first workflow of a chain, or ``None``."""
    if not chain:
        return None
    return getToolByName(context, "portal_workflow").getWorkflowById(chain[0])


def workflow_id(workflow):
    return workflow.getId() if workflow is not None else None


def source_states(workflow):
    """Return the ``(id, state)`` pairs of the states items can be in.

    Items of a type without a workflow are in a single state without ID.
    """
    if workflow is None:
        return [(NO_STATE, None)]
    return [(state.getId(), state) for state in workflow.states.objectValues()]


def suggest_state(source, target):
    """Return the state of the target workflow that keeps who can see items.

    Prefers the most visible state that isn't more visible than the source
    state, or else the least visible one. Among states equally visible, it
    prefers the same ID, then the same title, then the initial state.
    """
    if target is None:
        return None
    states = list(target.states.objectValues())
    if not states:
        return None
    ranks = {state.getId(): VISIBILITY_RANKS[visibility(state)] for state in states}
    rank = VISIBILITY_RANKS[visibility(source)] if source is not None else 0
    lower = [value for value in ranks.values() if value <= rank]
    rank = max(lower) if lower else min(ranks.values())
    candidates = [state for state in states if ranks[state.getId()] == rank]
    matches = (
        lambda state: source is not None and state.getId() == source.getId(),
        lambda state: source is not None and state.title == source.title,
        lambda state: state.getId() == target.initial_state,
    )
    for match in matches:
        for state in candidates:
            if match(state):
                return state.getId()
    return candidates[0].getId()


def check_state_map(state_map, target):
    """Return the errors of a state map for the target workflow.

    ``null`` targets get the suggested state.
    """
    if state_map is None:
        return []
    if not isinstance(state_map, dict):
        return [{"field": "state_map", "message": "Expected an object", "error": None}]
    states = set(target.states.objectIds()) if target is not None else set()
    return [
        {
            "field": "state_map",
            "message": f"Unknown state {new!r} for {old!r}",
            "error": None,
        }
        for old, new in sorted(state_map.items())
        if new is not None and new not in states
    ]


def _search(context, type_ids, **query):
    if not type_ids:
        return []
    catalog = getToolByName(context, "portal_catalog")
    return catalog.unrestrictedSearchResults(portal_type=list(type_ids), **query)


def count_unaffected(context, type_ids):
    """Count the items a placeful workflow policy gives another workflow.

    A change of the workflow of their type doesn't affect them.
    """
    if getToolByName(context, "portal_placeful_workflow", None) is None:
        return 0
    workflow_tool = getToolByName(context, "portal_workflow")
    return sum(
        1
        for brain in _search(context, type_ids)
        if tuple(workflow_tool.getChainFor(brain._unrestrictedGetObject()))
        != tuple(workflow_tool.getChainFor(brain.portal_type))
    )


def plan_change(context, type_ids, current, target):
    """Count the items of the types by current state, and suggest new states.

    The counts include items the current user cannot view.
    """
    states = []
    for state_id, state in source_states(current):
        query = {"review_state": state_id} if state is not None else {}
        states.append(
            {
                "id": state_id,
                "count": len(_search(context, type_ids, **query)),
                "suggested": suggest_state(state, target),
            }
        )
    return {"states": states, "unaffected": count_unaffected(context, type_ids)}


def apply_change(context, type_ids, chain, current, target, state_map=None):
    """Assign a workflow chain to the types, and remap the states of their items.

    ``chain`` is a tuple of workflow IDs, or ``DEFAULT_CHAIN``. States left out
    of ``state_map`` get the suggested state. Returns the number of remapped
    items, none when the workflow stays the same.
    """
    if not type_ids or workflow_id(current) == workflow_id(target):
        getToolByName(context, "portal_workflow").setChainForPortalTypes(
            type_ids, chain
        )
        return 0
    state_map = state_map or {}
    remapped = {
        # remap_workflow uses None for items without a workflow.
        state_id or None: state_map.get(state_id) or suggest_state(state, target)
        for state_id, state in source_states(current)
    }
    return remap_workflow(context, tuple(type_ids), chain, remapped)
