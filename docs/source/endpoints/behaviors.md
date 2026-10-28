---
myst:
  html_meta:
    "description": "List the behaviors that can be enabled on content types, and the fields they add, with the Plone REST API."
    "property=og:description": "List the behaviors that can be enabled on content types, and the fields they add, with the Plone REST API."
    "property=og:title": "Behaviors"
    "keywords": "Plone, plone.restapi, REST, API, behaviors, content types"
---

# Behaviors

The `@behaviors` service lists the behaviors that can be enabled on Dexterity content types.
It is available at the site root, and requires the `Plone Site Setup: Overview` permission, as well as permission to use the REST API.

Use the {doc}`content-types` service to enable behaviors on a content type, and to change their order.

## List behaviors

Send a `GET` request to `/@behaviors` to list every registered behavior.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/behaviors_get.req
```

The response contains `@id`, `items`, and `items_total`.
The items are sorted by name, and each has these properties:

| Property | Description |
| --- | --- |
| `name` | Behavior ID, as used in the `behaviors` of a content type. Behaviors without a short name use their interface identifier. |
| `title` | Translated title. |
| `description` | Translated description. |
| `fieldsets` | The fields the behavior adds to the edit form, by fieldset, each with an `id`, a `title`, and the names of its `fields`. Empty for behaviors that add no fields. |

Every behavior is listed once, although it is registered under its name and its interface identifier.

```json
{
  "name": "plone.leadimage",
  "title": "Lead Image",
  "description": "Adds image and image caption fields",
  "fieldsets": [
    {
      "id": "default",
      "title": "Default",
      "fields": ["image", "image_caption"]
    }
  ]
}
```
