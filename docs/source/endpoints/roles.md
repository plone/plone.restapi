---
myst:
  html_meta:
    "description": "Available roles in a Plone site can be queried by interacting with the /@roles endpoint on the portal root. This action requires an authenticated user."
    "property=og:description": "Available roles in a Plone site can be queried by interacting with the /@roles endpoint on the portal root. This action requires an authenticated user."
    "property=og:title": "Roles"
    "keywords": "Plone, plone.restapi, REST, API, Roles"
---

# Roles

Available roles in a Plone site can be queried by interacting with the `/@roles` endpoint on the portal root.
This action requires an authenticated user.


## List Roles

To retrieve a list of all roles in the portal, call the `/@roles` endpoint with a `GET` request:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/roles.req
```

The server will respond with a list of all roles in the portal:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/roles.resp
:language: http
```

The role `title` is the translated role title as displayed in Plone's {guilabel}`Users and Groups` control panel.
