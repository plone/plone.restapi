---
myst:
  html_meta:
    "description": "The @querystring endpoint returns the querystring configuration of plone.app.querystring."
    "property=og:description": "The @querystring endpoint returns the querystring configuration of plone.app.querystring."
    "property=og:title": "Querystring"
    "keywords": "Plone, plone.restapi, REST, API, Querystring"
---

# Querystring

The `@querystring` endpoint returns the `querystring` configuration of `plone.app.querystring`.

Instead of simply exposing the `querystring` related `field` and `operation` entries from the registry, it serializes them in the same way that `p.a.querystring` does in its `@@querybuilderjsonconfig` view.

This form is structured in a more convenient way for frontends to process:

- *Vocabularies* will be resolved.
  Their values will be inlined in the `values` property.
- *Operations* will be inlined as well.
  The `operations` property will contain the list of operations as dotted names.
  The `operators` property will contain the full definition of each of those operations supported by that field.
- Indexes that are flagged as *sortable* are listed in a dedicated top-level property `sortable_indexes`.

Available options for the querystring in a Plone site can be queried by interacting with the `/@querystring` endpoint on the portal root:


## Querystring Config

To retrieve all `querystring` options in the portal, call the `/@querystring` endpoint with a `GET` request:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/querystring_get.req
```

The server will respond with all `querystring` options in the portal:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/querystring_get.resp
:language: http
```
