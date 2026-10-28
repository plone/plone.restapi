---
myst:
  html_meta:
    "description": "List the workflows that can be assigned to content types, and change the default workflow, with the Plone REST API."
    "property=og:description": "List the workflows that can be assigned to content types, and change the default workflow, with the Plone REST API."
    "property=og:title": "Workflows"
    "keywords": "Plone, plone.restapi, REST, API, workflows, content types"
---

# Workflows

The `@workflows` service describes the workflows that can be assigned to content types, and changes the site's default workflow.
It is available at the site root, and requires the `Plone Site Setup: Overview` permission, as well as permission to use the REST API.

Use the {doc}`content-types` service to change the workflow of a content type, and the {doc}`workflow` service to change the state of an item.

| Method | Path | Result |
| --- | --- | --- |
| `GET` | `/@workflows` | Every workflow, and the default workflow. |
| `GET` | `/@workflows/{id}` | One workflow with its states and transitions. |
| `POST` | `/@workflows` | Change the default workflow. |

## List workflows

Send a `GET` request to `/@workflows` to list every workflow.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflows_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflows_get.resp
:language: http
```

The response contains `@id`, `default`, and `items`.
`default` is the ID of the default workflow, or `null` when there is none.
The items are sorted by title, and each has these properties:

| Property | Description |
| --- | --- |
| `@id` | URL of the workflow in this service. |
| `id` | Workflow ID. |
| `title` | Translated title. |
| `description` | Translated description. |
| `initial_state` | ID of the state of new items. |
| `states` | IDs of the states, in the order of the workflow. |

## Get a workflow

Send a `GET` request to `/@workflows/{id}` to get one workflow with its states and transitions.
Unknown workflows return `404 Not Found`.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflows_get_item.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflows_get_item.resp
:language: http
```

The response has the properties of the listing, and these:

| Property | Description |
| --- | --- |
| `states` | The states, each with an `id`, a translated `title` and `description`, the IDs of the `transitions` leaving it, its `visibility`, and its `permission_roles`. |
| `transitions` | The transitions, each with an `id`, a translated `title` and `description`, the ID of its `new_state`, and its `guard`, with `permissions`, `roles`, and an `expression`. |
| `types` | IDs of the content types using the workflow, including those following the default workflow. |

`permission_roles` maps each permission the state manages to the roles that have it.
`visibility` summarizes who can see items in the state, from the roles with the `View` permission:

| Value | Who can see items |
| --- | --- |
| `anyone` | Anonymous visitors. |
| `members` | Authenticated users. The roles include `Authenticated` or `Member`. |
| `restricted` | Only the roles listed, such as `Owner`, `Reviewer`, or `Manager`. |
| `unknown` | The state doesn't manage `View`, or it acquires the permission, so it depends on the container. |

## Change the default workflow

Send a `POST` request to `/@workflows` to change the default workflow.
It affects every content type that follows the default.
The body has these properties:

| Property | Description |
| --- | --- |
| `default` | ID of the new default workflow, or `null` for no default workflow. Required. |
| `state_map` | Maps the states of the current default workflow to states of the new one. Optional. |
| `dry_run` | When `true`, changes nothing, and returns the planned change. |

Unknown workflows and unknown target states return `400 Bad Request`.

### Plan the change

With `dry_run`, the service returns the number of items in each state, and a suggested new state for each.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflows_post_dry_run.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflows_post_dry_run.resp
:language: http
```

| Property | Description |
| --- | --- |
| `workflow` | ID of the new workflow, or `null`. |
| `current` | ID of the current workflow, or `null`. |
| `states` | One entry per state of the current workflow, in its order, with the state `id`, the `count` of items in it, and the `suggested` new state. |
| `unaffected` | Number of items that a placeful workflow policy gives another workflow, which the change doesn't affect. |
| `types` | IDs of the content types following the default workflow. |

Without a current workflow, `states` has a single entry with an empty `id`, counting every item of the types.
The counts include items the current user cannot view.
`suggested` is `null` when the new workflow is `null`.

The suggested state keeps who can see the items.
It's the most visible state of the new workflow that isn't more visible than the current state, comparing their `visibility` (`unknown` and `restricted` are the least visible, then `members`, then `anyone`).
If every state is more visible, it's the least visible one.
Among equally visible states, the service prefers the one with the same ID, then the one with the same title, then the initial state, then the first state.

### Apply the change

Without `dry_run`, the service changes the default workflow, moves the items of the types following it to their new states, and updates their security.
States left out of `state_map` get the suggested state.
The change happens during the request, as in the classic control panel, so it can take long on large sites.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflows_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflows_post.resp
:language: http
```

The response contains the new `default` and the number of `changed` items.
