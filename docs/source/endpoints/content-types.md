---
myst:
  html_meta:
    "description": "List, configure, create, copy, and delete content types with the Plone REST API."
    "property=og:description": "List, configure, create, copy, and delete content types with the Plone REST API."
    "property=og:title": "Content type management"
    "keywords": "Plone, plone.restapi, REST, API, content types, FTI, settings"
---

# Content type management

The `@content-types` service lists, configures, creates, copies, and deletes content types.
It is available at the site root, and requires the `Plone Site Setup: Overview` permission, as well as permission to use the REST API.

Use the {doc}`types` service to edit the schema of a content type.
The `dexterity-types` control panel of the {doc}`controlpanels` service remains available.

```{seealso}
This page used to show example representations of the default content types.
They are now in {ref}`content-default-types-representations`.
```

| Method | Path | Result |
| --- | --- | --- |
| `GET` | `/@content-types` | Every content type with its settings. |
| `GET` | `/@content-types/{type}` | One content type with its settings. |
| `POST` | `/@content-types` | Create a Dexterity content type, optionally copying another one. |
| `PATCH` | `/@content-types/{type}` | Change some settings of a content type. |
| `DELETE` | `/@content-types/{type}` | Delete a Dexterity content type that has no items. |
| `GET` | `/@content-types/{type}/workflow` | The workflow of a content type. |
| `POST` | `/@content-types/{type}/workflow` | Change the workflow of a content type. |

Encode content type IDs in URLs, for example `News%20Item`.
Unknown content types and extra path segments return `404 Not Found`.

## List content types

Send a `GET` request to `/@content-types` to list every content type with its settings.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_get.req
```

The response contains `@id`, `items`, and `items_total`.
Each item has the representation of a single content type, described below.

## Get a content type

Send a `GET` request to `/@content-types/{type}` to get one content type.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_get_item.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_get_item.resp
:language: http
```

| Property | Description |
| --- | --- |
| `@id` | URL of the content type in this service. |
| `id` | Content type ID. |
| `title` | Translated title. |
| `items_total` | Number of items of this type, including those the current user cannot view. |
| `schema` | JSON schema of the settings, with `properties`, `required`, and `fieldsets`, in the same format as the {doc}`controlpanels` service. |
| `data` | Current values of the settings, keyed by field name. |
| `workflow` | Read-only summary of the assigned workflow. |

Each fieldset has an `id`, a `title`, and the names of its `fields`.
Fields marked `readOnly` in the schema cannot be changed.
Choice values have a `token` and a `title`, like in control panels and content.

`workflow.id` is the first workflow of the type's chain, or `null` when the type has no workflow.
`workflow.follows_default` is `true` when the type uses the site's default workflow, and `false` when a workflow, or no workflow, is assigned to it explicitly.
It changes through `/@content-types/{type}/workflow`, described in {ref}`content-types-workflow`.

### Core settings

| Fieldset | Field | Value |
| --- | --- | --- |
| `general` | `title` | Title, not empty. |
| `general` | `description` | Description. |
| `contents` | `global_allow` | Whether items of this type can be added in any folder. |
| `contents` | `allowed_content_types_mode` | Which types can be added inside items of this type: `all`, `selected`, or `none`. |
| `contents` | `allowed_content_types` | IDs of the selected types. |
| `visibility` | `searchable` | Whether items of this type are shown in search results. |
| `visibility` | `default_page` | Whether items of this type can be a folder's default page. |
| `comments` | `allow_discussion` | Whether items of this type allow comments. |
| `behaviors` | `behaviors` | IDs of the type's behaviors, in order. Dexterity types only. |
| `versioning` | `versioning` | `off`, `manual`, or `automatic`. |

`allowed_content_types_mode` and `allowed_content_types` work together:

- `all` allows every type. `allowed_content_types` keeps the selection, which applies when you change the mode to `selected` later.
- `selected` allows only the types in `allowed_content_types`, which can't be empty.
- `none` allows no types, and `allowed_content_types` must be empty.

The service checks these rules against the stored values too, so changing only the mode to `none` fails while types are selected.

`manual` versioning saves versions on request, and `automatic` versioning also saves a version on every edit.
Changing the versioning updates the repository policies of the type and its versioning behavior.
Enabling versioning also enables locking, and disabling versioning keeps locking.
Repository policies added by add-ons are kept.

`behaviors` is the complete, ordered list of the type's behaviors.
Their order sets where their fields appear in the edit form.
Behaviors are listed by their name, such as `plone.dublincore`, also when the type stores the interface identifier.
A `PATCH` replaces the list: a behavior left out is disabled.
Behaviors stored on the type that aren't registered, for example those of an uninstalled add-on, aren't listed and are kept.
In a `PATCH` that changes `behaviors` and `versioning`, the versioning setting decides whether the type has the versioning behavior.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_patch_behaviors.req
```

Use the {doc}`behaviors` service to list the behaviors and the fields they add, and the `behaviors` parameter of the {doc}`types` service to preview the edit form with other behaviors.

## Change settings

Send a `PATCH` request to `/@content-types/{type}` with the fields to change.
Fields you don't send keep their values.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_patch.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_patch.resp
:language: http
```

A choice value can be its token, or an object with a `token`, as returned in `data`.

The service validates every change before it stores any of them.
Invalid values, unknown fields, and read-only fields return `400 Bad Request` with the field names and messages.

(content-types-workflow)=

## Change the workflow

Send a `GET` request to `/@content-types/{type}/workflow` to get the workflow of a content type.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_get_workflow.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_get_workflow.resp
:language: http
```

It has the same `id` and `follows_default` as the `workflow` of the content type.

Send a `POST` request to `/@content-types/{type}/workflow` to change it.
The body has these properties:

| Property | Description |
| --- | --- |
| `workflow` | ID of the new workflow, or `null` for no workflow. |
| `follows_default` | When `true`, the type follows the default workflow again, and `workflow` is ignored. |
| `state_map` | Maps the states of the current workflow to states of the new one. Use `""` for items of a type without a workflow. Optional. |
| `dry_run` | When `true`, changes nothing, and returns the planned change. |

The body needs `workflow` or `follows_default`.
Unknown workflows and unknown target states return `400 Bad Request`.
The service changes one content type at a time.
Use the {doc}`workflows` service to list the workflows, their states and who can see items in them, and to change the default workflow.

### Plan the change

With `dry_run`, the service returns the number of items of the type in each state, and a suggested new state for each.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_post_workflow_dry_run.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_post_workflow_dry_run.resp
:language: http
```

| Property | Description |
| --- | --- |
| `workflow` | ID of the new workflow, which is the default workflow with `follows_default`, or `null`. |
| `current` | ID of the current workflow, or `null`. |
| `states` | One entry per state of the current workflow, in its order, with the state `id`, the `count` of items in it, and the `suggested` new state. |
| `unaffected` | Number of items that a placeful workflow policy gives another workflow, which the change doesn't affect. |

Without a current workflow, `states` has a single entry with an empty `id`, counting every item of the type.
The counts include items the current user cannot view.
`suggested` is `null` when the new workflow is `null`.
The suggested state keeps who can see the items, as described in {doc}`workflows`.

### Apply the change

Without `dry_run`, the service assigns the workflow, moves the items of the type to their new states, and updates their security, as the classic "Content Settings" control panel does.
States left out of `state_map` get the suggested state.
The change happens during the request, so it can take long for types with many items.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_post_workflow.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_post_workflow.resp
:language: http
```

The response contains the new `workflow`, whether the type `follows_default`, and the number of `changed` items.
When the workflow stays the same, for example when a type following the default gets the default workflow explicitly, only the assignment changes, and `changed` is `0`.

## Create a content type

Send a `POST` request to `/@content-types` to create a Dexterity container type with an empty schema.
The body requires a `title`, and accepts an `id` and a `description`.
Without an `id`, the service derives one from the title.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_post.resp
:language: http
```

The new type has the same defaults as one created in the classic "Dexterity Content Types" control panel.
The service returns `409 Conflict` when a type with the ID exists.

### Copy a content type

Add `copy_from` with the ID of a Dexterity content type to copy it.
The copy has the schema, behaviors, settings, actions, repository policies, and workflow assignment of the source.
Without a `description`, it also has the source's description.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_copy.req
```

Changes to the copy, including to its schema, don't affect the source.

## Delete a content type

Send a `DELETE` request to `/@content-types/{type}` to delete a Dexterity content type.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/content_types_delete.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_delete.resp
:language: http
```

Deleting a type also removes its settings, its workflow assignment, and its use as an allowed type of other types.
A type created later with the same ID starts with default settings.

While items of the type exist, the service returns `409 Conflict` with their number.

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/content_types_delete_nonempty.resp
:language: http
```

## Add settings from an add-on

Each fieldset comes from a named adapter providing `plone.restapi.typesettings.interfaces.ITypeSettings`.
The core fieldsets use the same mechanism, so an add-on can add its own settings to every content type.
Because the response includes a JSON schema, a frontend can show them without knowing the add-on.

An adapter adapts the FTI and the request, and has these attributes and methods:

| Name | Description |
| --- | --- |
| `title` | Fieldset title. |
| `order` | Sort order of the fieldset, lowest first. The core fieldsets use 10 to 50. |
| `schema` | `zope.schema` interface declaring the fields. Field names must be unique across all fieldsets. |
| `permission` | Permission ID needed to see and change the fieldset, or `None`. |
| `read()` | Return the current values. |
| `validate(data)` | Return a list of errors for the changed values, each with `field` and `message`. |
| `write(data)` | Store the changed values. |
| `remove()` | Delete what the settings store outside the FTI, before the type is deleted. |

The service converts values with the registered field serializers and deserializers, and validates them with the field constraints and the schema invariants.
It applies `plone.autoform` directives such as `omitted`, `mode`, and `order_before`.
Use flat fields: values of `schema.Object` fields aren't converted to and from JSON.

Subclass `plone.restapi.typesettings.settings.TypeSettings` to store settings as FTI properties, or override its methods to store them elsewhere.
This example stores a setting in the registry:

```python
from plone.registry.interfaces import IRegistry
from plone.restapi.typesettings.settings import TypeSettings
from zope import schema
from zope.component import getUtility
from zope.interface import Interface


class ISponsorSettings(Interface):
    sponsors_enabled = schema.Bool(title="Show sponsors")


class SponsorSettings(TypeSettings):
    title = "Sponsors"
    order = 100
    schema = ISponsorSettings
    record = "collective.sponsors.types"

    def read(self):
        types = getUtility(IRegistry)[self.record]
        return {"sponsors_enabled": self.context.getId() in types}

    def write(self, data):
        registry = getUtility(IRegistry)
        types = set(registry[self.record]) - {self.context.getId()}
        if data["sponsors_enabled"]:
            types.add(self.context.getId())
        registry[self.record] = sorted(types)

    def remove(self):
        self.write({"sponsors_enabled": False})
```

```xml
<adapter
    factory=".settings.SponsorSettings"
    name="collective.sponsors"
    />
```
