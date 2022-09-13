---
myst:
  html_meta:
    "description": "The principal endpoint will search for all the available principals in the local PAS plugins when given a query string. We define a principal as any user or group in the system."
    "property=og:description": "The principal endpoint will search for all the available principals in the local PAS plugins when given a query string. We define a principal as any user or group in the system."
    "property=og:title": "Principals"
    "keywords": "Plone, plone.restapi, REST, API, Principals"
---

# Principals

This endpoint will search for all the available principals in the local PAS plugins when given a query string.
We define a principal as any user or group in the system.
This endpoint requires an authenticated user.


## Search Principals

To retrieve a list of principals given a search string, call the `/@principals` endpoint with a `GET` request and a `search` query parameter:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/principals.req
```

The server will respond with a list of the users and groups in the portal that match the query string:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/principals.resp
:language: http
```
