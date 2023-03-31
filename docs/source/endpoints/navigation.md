---
myst:
  html_meta:
    "description": "Get the top-level navigation items or navigation item tree with the navigation endpoint."
    "property=og:description": "Get the top-level navigation items or navigation item tree with the navigation endpoint."
    "property=og:title": "Navigation"
    "keywords": "Plone, plone.restapi, REST, API, Navigation"
---

(navigation)=

# Navigation


## Top-Level Navigation

Get the top-level navigation items:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navigation.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navigation.resp
:language: http
```


## Navigation Tree

Get the navigation item tree by providing a `expand.navigation.depth` parameter:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navigation_tree.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navigation_tree.resp
:language: http
```
