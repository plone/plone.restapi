---
myst:
  html_meta:
    "description": "Control panels in Plone allow you to configure the global site setup of a Plone site. The @controlpanels endpoint in plone.restapi allows you to list all existing control panels in a Plone site, and to retrieve or edit the settings of a specific control panel."
    "property=og:description": "Control panels in Plone allow you to configure the global site setup of a Plone site. The @controlpanels endpoint in plone.restapi allows you to list all existing control panels in a Plone site, and to retrieve or edit the settings of a specific control panel."
    "property=og:title": "Control Panels"
    "keywords": "Plone, plone.restapi, REST, API, Control, Panels"
---

# Control Panels

Control panels in Plone allow you to configure the global site setup of a Plone site.
The `@controlpanels` endpoint in `plone.restapi` allows you to list all existing control panels in a Plone site, and to retrieve or edit the settings of a specific control panel.

Most of the settings in the Plone control panels are based on `plone.registry` since Plone 5.x.
Therefore, you can also use the `@registry` endpoint to retrieve or manipulate site settings.
The `@controlpanels` endpoint is a more convenient way of accessing the settings, and makes it
easier to render control panels on the front-end.

```{note}
The `@controlpanels` endpoint is implemented for Plone 5 or greater.
```


## Listing Control Panels

A list of all existing control panels in the portal can be retrieved by sending a `GET` request to the `@controlpanels` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_get.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_get.resp
:language: http
```

The following fields are returned:

- `@id`: hypermedia link to the control panel
- `title`: the title of the control panel
- `group`: the group in which the control panel should appear, for example, `General`, `Content`, `Users`, `Security`, `Advanced`, or `Add-on Configuration`.


## Retrieve a single Control Panel

To retrieve a single control panel, send a `GET` request to the URL of the control panel:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_get_item.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_get_item.resp
:language: http
```

The following fields are returned:

- `@id`: hypermedia link to the control panel
- `title`: title of the control panel
- `group`: group name of the control panel
- `schema`: JSON Schema of the control panel
- `data`: current values of the control panel


## Updating a Control Panel with `PATCH`

To update the settings on a control panel, send a `PATCH` request to control panel resource:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_patch.req
```

A successful response to a `PATCH` request will be indicated by a {term}`204 No Content` response:


```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_patch.resp
:language: http
```


## Control Panels not based on `plone.registry`

Control panels which are not based on `plone.registry` have a custom `@controlpanels/:panel` endpoint implementation.


(dexterity-types)=

### Dexterity Types

`@controlpanels/dexterity-types` is a custom control panel endpoint that will allow you to add, remove, and configure available {ref}`types`.

Reading or writing Dexterity content types require the `plone.schemaeditor.ManageSchemata` permission.

| Verb     | URL                                         | Action                                    |
| -------- | ------------------------------------------- | ----------------------------------------- |
| `GET`    | `/@controlpanels/dexterity-types`           | List configurable content types           |
| `POST`   | `/@controlpanels/dexterity-types`           | Creates a new content type                |
| `GET`    | `/@controlpanels/dexterity-types/{type-id}` | Get the current state of the content type |
| `PATCH`  | `/@controlpanels/dexterity-types/{type-id}` | Update the content type details           |
| `DELETE` | `/@controlpanels/dexterity-types/{type-id}` | Remove the content type                       |


#### Listing Dexterity Content Types

To list the available content types, send a `GET` request to `@controlpanels/dexterity-types`

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity.resp
:language: http
```

The following fields are returned:

- `@id`: hypermedia link to the control panel
- `title`: title of the control panel
- `group`: group name of the control panel
- `schema`: JSON Schema of the control panel
- `data`: current values of the control panel
- `items`: list of configurable content types


#### Creating a new Dexterity Type with `POST`

To create a new content type, send a `POST` request to the `/@controlpanels/dexterity-types` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_post_dexterity_item.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_post_dexterity_item.resp
:language: http
```


#### Reading a Dexterity Type with `GET`

After a successful `POST`, access the content type by sending a `GET` request to the endpoint `/@controlpanels/dexterity-types/{type-id}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity_item.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity_item.resp
:language: http
```


#### Updating a Dexterity Type with `PATCH`

To update an existing content type, send a `PATCH` request to the server.
`PATCH` allows to provide just a subset of the resource, that is, the values you actually want to change:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_dexterity_item.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_dexterity_item.resp
:language: http
```


#### Removing a Dexterity Type with `DELETE`

Delete an existing content type by sending a `DELETE` request to the URL of an existing content type:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_dexterity_item.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_dexterity_item.resp
:language: http
```

### Content rules

`@controlpanels/content-rules` is a custom control panel endpoint that will allow you to add, remove, and configure available {doc}`content-rules`.

| Verb     | URL                                         | Action                                    |
| -------- | ------------------------------------------- | ----------------------------------------- |
| `GET`    | `/@controlpanels/content-rules`             | List configurable content rules           |
| `POST`   | `/@controlpanels/content-rules`             | Creates a new content rule                |
| `GET`    | `/@controlpanels/content-rules/{rule-id}`   | Get the current state of the content rule |
| `PATCH`  | `/@controlpanels/content-rules/{rule-id}`   | Update the content rule details           |
| `DELETE` | `/@controlpanels/content-rules/{rule-id}`   | Remove the content rule                   |


#### Listing Content Rules

To list the available content rules, send a `GET` request to `@controlpanels/content-rules`

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_get_contentrules.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_get_contentrules.resp
:language: http
```

The following fields are returned:

- `@id`: hypermedia link to the rule
- `id`: actual id of the content rule
- `assigned`: rule assigned or not
- `title`: title of the rule
- `description`: rule description
- `enabled`: rule is enabled or not
- `trigger`: triggering event
- `conditions`: conditions before triggering the rule
- `actions`: actions to take place


#### Creating a new Content rule with `POST`

To create a new content rule, send a `POST` request to the `/@controlpanels/content-rules` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_post_rule.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_post_rule.resp
:language: http
```


#### Creating a new Condition on a Content rule with `POST`

To create a new condition on a content rule, send a `POST` request to the
`/@controlpanels/content-rules/{rule-id}/condition` endpoint, specifying the
condition type in the payload:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_post_rule_condition_portaltype.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_post_rule_condition_portaltype.resp
:language: http
```


#### Creating a new Action on a Content rule with `POST`

To create a new action on a content rule, send a `POST` request to the
`/@controlpanels/content-rules/{rule-id}/action` endpoint, specifying the
action type in the payload:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_post_rule_action_logger.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_post_rule_action_logger.resp
:language: http
```


#### Reading a Content rule with `GET`

After a successful `POST`, access the content rule by sending a `GET` request to the endpoint `/@controlpanels/content-rules/{rule-id}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_get_rule.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_get_rule.resp
:language: http
```


#### Updating a Content rule with `PATCH`

To update an existing content rule, send a `PATCH` request to the server.
`PATCH` allows to provide just a subset of the resource, that is, the values you actually want to change:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_rule.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_rule.resp
:language: http
```

#### Updating a Condition on a Content rule with `PATCH`

To update an existing condition on a content rule, send a `PATCH` request to the server.
`PATCH` allows to provide just a subset of the resource, that is, the values you actually want to change:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_rule_condition_portaltype.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_rule_condition_portaltype.resp
:language: http
```

### Updating an Action on a Content rule with `PATCH`

To update an existing action on a content rule, send a `PATCH` request to the server.
`PATCH` allows to provide just a subset of the resource, that is, the values you actually want to change:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_rule_action_logger.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_patch_rule_action_logger.resp
:language: http
```


#### Removing a Content rule with `DELETE`

Delete an existing content rule by sending a `DELETE` request to the URL of an existing content rule:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_rule.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_rule.resp
:language: http
```

#### Removing a Condition on a Content rule with `DELETE`

Delete an existing condition from a content rule by sending a `DELETE` request to the URL of an existing content rule:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_rule_condition.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_rule_condition.resp
:language: http
```

#### Removing an Action on a Content rule with `DELETE`

Delete an existing action from a content rule by sending a `DELETE` request to the URL of an existing content rule:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_rule_condition.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/controlpanels_delete_rule_condition.resp
:language: http
```
