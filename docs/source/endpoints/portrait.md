---
myst:
  html_meta:
    "description": "Returns user's portrait in a Plone site using the @portrait endpoint"
    "property=og:description": "Returns user's portrait in a Plone site using the @portrait endpoint"
    "property=og:title": "Portraits"
    "keywords": "Plone, plone.restapi, REST, API, Users, portrait, profile"
---

# Portraits

Plone users have the option to upload a portrait to their profile. This profile is used in several places in Plone's user interface, like in the comments view.

## Get self portrait

You can request your own user portrait by issuing a `GET` request to the root URL appending `/@portrait`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/portrait_self_get.req
```

The server will respond with a `Status 200` and the image requested (not JSON). The content type is set accordingly. One can use it directly in HTML `src` properties:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/portrait_self_get.resp
:language: http
```

The server will respond with a `Status 404` in case that the portrait is not set.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/portrait_self_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/portrait_self_404_get.resp
:language: http
```

## Get specific user portrait

You can request the portrait for a specific user `username` by issuing a `GET` request to the root URL appending `/@portrait/username`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/portrait_username_get.req
```

The server will respond with a `Status 200` and the image requested (not JSON). The content type is set accordingly. One can use it directly in HTML `src` properties:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/portrait_username_get.resp
:language: http
```
