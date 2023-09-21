---
myst:
  html_meta:
    "description": "The @querystring endpoint returns metadata about available query operations."
    "property=og:description": "The @querystring endpoint returns metadata about available query operations."
    "property=og:title": "Querystring"
    "keywords": "Plone, plone.restapi, REST, API, Querystring"
---

# Querystring

The `@querystring` endpoint returns metadata about the query operations that can be performed using the [`@querystringsearch`](querystringsearch) endpoint.

The results include all of the indexes that can be queried, along with metadata about each index.
The top-level `indexes` property includes all indexes, and the top-level `sortable_indexes` property includes only the indexes that can be used to sort.

Each index result includes a list of the query operations that can be performed on that index.
The `operations` property contains the list of operations as dotted names.
The `operators` property contains additional metadata about each operation.

If an index uses a vocabulary, the vocabulary values are included in the `values` property.
The vocabulary is resolved in the same context where the `/@querystring` endpoint is called (requires `plone.app.querystring >= 2.1.0`).

## Get `querystring` configuration

To get the metadata about all query operations available in the portal, call the `/@querystring` endpoint with a `GET` request:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/querystring_get.req
```

The server will respond with the metadata:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/querystring_get.resp
:language: http
```
