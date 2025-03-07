---
myst:
  html_meta:
    "description": "Registry records can be addressed through the @registry endpoint on the Plone site."
    "property=og:description": "Registry records can be addressed through the @registry endpoint on the Plone site."
    "property=og:title": "Registry"
    "keywords": "Plone, plone.restapi, REST, API, Registry"
---

# Registry

Registry records can be addressed through the `@registry` endpoint on the Plone site.
To address a specific record, the fully qualified dotted name of the registry record has to be passed as a path segment, for example, `/plone/@registry/my.record`.

Reading or writing registry records require the `cmf.ManagePortal` permission.


## Reading registry records

Reading a single record:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/registry_get.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/registry_get.resp
:language: http
```


## Listing registry records

The registry records listing uses a batched method to access all registry records.
See {doc}`../usage/batching` for more details on how to work with batched results.

The output record contains the following fields:

- `name`: The record's fully qualified dotted name.
- `value`: The record's value. This is the same as `GET`ting `@registry/name`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/registry_get_list.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/registry_get_list.resp
:language: http
```

## Filter list of registry records

```{versionadded} plone.restapi 9.10.0
```

You can filter a list of registry records and batch the results.
To do so, append a query string to the listing endpoint with a `q` parameter and its value set to the prefix of the desired record name.
See {doc}`../usage/batching` for details of how to work with batched results.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/registry_get_list_filtered.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/registry_get_list_filtered.resp
:language: http
```

## Updating registry records

Updating an existing record:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/registry_update.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/registry_update.resp
:language: http
```
