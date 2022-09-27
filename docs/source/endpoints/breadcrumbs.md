---
myst:
  html_meta:
    "description": "Get the breadcrumbs for the current page with plone.restapi."
    "property=og:description": "Get the breadcrumbs for the current page with plone.restapi."
    "property=og:title": "Breadcrumbs"
    "keywords": "Plone, plone.restapi, REST, API, Breadcrumbs"
---

(breadcrumbs)=

# Breadcrumbs

Get the breadcrumbs for the current page:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/breadcrumbs.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/breadcrumbs.resp
:language: http
```
