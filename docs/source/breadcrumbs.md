---
html_meta:
  "description": ""
  "property=og:description": ""
  "property=og:title": ""
  "keywords": "Plone, plone.restapi, REST, API"
---

(breadcrumbs)=

# Breadcrumbs

Get the breadcrumbs for the current page:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/breadcrumbs.req
```

Example response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/breadcrumbs.resp
:language: http
```
