---
myst:
  html_meta:
    "description": "Aliases - a mechanism to redirect old URLs to new ones."
    "property=og:description": "Aliases - a mechanism to redirect old URLs to new ones."
    "property=og:title": "Aliases"
    "keywords": "Plone, plone.app.redirector, redirector, REST, API, Aliases"
---

# Aliases

A mechanism to redirect old URLs to new ones.

When an object is moved (renamed or cut/pasted into a different location), the redirection storage will remember the old path. It is smart enough to deal with transitive references (if we have a -> b and then add b -> c, it is replaced by a reference a -> c) and circular references (attempting to add a -> a does nothing).

The API consumer can create, read, and delete aliases.


| Verb     | URL         | Action                                 |
| -------- | ----------- | -------------------------------------- |
| `POST`   | `/@aliases` | Add one or more aliases                |
| `GET`    | `/@aliases` | List all aliases                       |
| `DELETE` | `/@aliases` | Remove one or more aliases             |

## Adding new URL aliases for a Page

By default, Plone automatically creates a new alias when an object is renamed or moved. Still, you can also create aliases manually.

To create a new alias, send a `POST` request to the `/@aliases` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_add.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_add.resp
:language: http
```

## Listing URL aliases of a Page

To list aliases, you can send a `GET` request to the `/@aliases` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_get.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_get.resp
:language: http
```


## Removing URL aliases of a Page

To remove aliases, send a `DELETE` request to the `/@aliases` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_delete.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_delete.resp
:language: http
```

## Adding URL aliases in bulk

You can add multiple URL aliases for multiple pages by sending a `POST` request to the `/@aliases` endpoint on site `root`. **datetime** parameter is optional:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_root_add.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_root_add.resp
:language: http
```


## Listing all available aliases

To list all aliases, send a `GET` request to the `/@aliases` endpoint on site `root`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_root_get.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_root_get.resp
:language: http
```

## Filter aliases

To search for specific aliases, send a `GET` request to the `/@aliases` endpoint on site `root` with a `q` parameter:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_root_filter.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_root_filter.resp
:language: http
```


## Bulk removing aliases

To bulk remove aliases send a `DELETE` request to the `/@aliases` endpoint on site `root`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/aliases_root_delete.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/aliases_root_delete.resp
:language: http
```
