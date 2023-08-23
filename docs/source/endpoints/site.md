---
myst:
  html_meta:
    "description": "Site endpoint for Plone REST API"
    "property=og:title": "Site endpoint for Plone REST API"
    "property=og:description": "Site endpoint for Plone REST API"
    "keywords": "Plone, plone.restapi, REST, API, site, navigation root"
---

# Site

The `@site` endpoint provides general site-wide information, such as the site title, logo, and other information.
It uses the `zope2.View` permission, which requires appropriate authorization.

Send a `GET` request to the `@site` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/site_get.req
```

The response will contain the site information:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/site_get.resp
:language: http
```
