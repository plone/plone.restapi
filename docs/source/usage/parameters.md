---
myst:
  html_meta:
    "description": "URL parameters accepted by the Plone REST API."
    "property=og:description": "URL parameters accepted by the Plone REST API."
    "property=og:title": "URL Parameters"
    "keywords": "Plone, plone.restapi, REST, API, parameters, boolean"
---

(restapi-parameters)=

# Parameters

This chapter describes the conventions for URL parameters accepted by the Plone REST API.

(boolean-parameters)=

## Boolean Parameters

```{versionchanged} plone.restapi 10.0.0
Since plone.restapi version 10.0.0, boolean parameters are validated more strictly.
```

The following strings represent a boolean value of `True`.

- 1
- y
- yes
- t
- true
- True
- active
- enabled
- on

The following strings represent a boolean value of `False`.

- 0
- n
- no
- f
- false
- False
- inactive
- disabled
- off

Any other value will return a `400 Bad Request` response.
