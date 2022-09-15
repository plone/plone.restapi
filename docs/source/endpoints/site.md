---
html_meta:
  "description": "Site endpoint for Plone REST API"
  "property=og:title": "Site endpoint for Plone REST API"
  "property=og:description": "Site endpoint for Plone REST API"
  "keywords": "Plone, plone.restapi, REST, API, site, navigation root"
---

# Site

The `@site` endpoint provides site-wide information, such as the site title, logo, and other information, which is useful to offer generic information about the Plone site.

Send a `GET` request to the `@site` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/site_get.req
```

The response will contain the site information:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/site_get.resp
:language: http
```
