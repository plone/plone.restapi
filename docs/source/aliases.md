---
html_meta:
  "description": "Aliases is a mechanism to redirect old URLs to new ones."
  "property=og:description": "Aliases is a mechanism to redirect old URLs to new ones."
  "property=og:title": "Aliases"
  "keywords": "Plone, plone.app.redirector, redirector, REST, API, Aliases"
---

# Aliases

Aliases is a mechanism to redirect old URLs to new ones.

When an object is moved (renamed or cut/pasted into a different location), the redirection storage will remember the old path. It is smart enough to deal with transitive references (if we have a -> b and then add b -> c, it is replaced by a reference a -> c) and circular references (attempting to add a -> a does nothing).

The API consumer can create, read, and delete aliases.


| Verb     | URL         | Action                                 |
| -------- | ----------- | -------------------------------------- |
| `POST`   | `/@aliases` | Add one or more aliases                |
| `GET`    | `/@aliases` | List all aliases                       |
| `DELETE` | `/@aliases` | Remove one or more aliases             |

## Adding new aliases on a Content Object

By default, Plone automatically creates a new alias when an object is renamed or moved. Still, you can also create aliases manually.

To create a new alias, send a POST request to the `/@aliases` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/aliases_add.req
```

Response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/aliases_add.resp
:language: http
```

## Listing aliases of a Content Object

Listing aliases of a resource you can send a `GET` request to the `/@aliases` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/aliases_get.req
```

Response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/aliases_get.resp
:language: http
```


## Removing aliases of a Content Object

To remove aliases of an object, send a `DELETE` request to the `/@aliases` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/aliases_delete.req
```

Response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/aliases_delete.resp
:language: http
```
