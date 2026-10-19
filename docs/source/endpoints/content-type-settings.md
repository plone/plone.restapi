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

| Method | Path | Result |
| --- | --- | --- |
| `GET` | `/@content-types` | Every content type with its settings. |
| `GET` | `/@content-types/{type}` | One content type with its settings. |
| `POST` | `/@content-types` | Create a Dexterity content type, optionally copying another one. |
| `PATCH` | `/@content-types/{type}` | Change some settings of a content type. |
| `DELETE` | `/@content-types/{type}` | Delete a Dexterity content type that has no items. |

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
