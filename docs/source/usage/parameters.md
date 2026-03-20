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

## Boolean Parameters

```{versionchanged} plone.restapi 10.0.0
Since plone.restapi version 10.0.0, boolean parameters are validated more strictly.
```

Values that evaluate as `True`, where quoted values are strings, and unquoted values are either boolean or integer.

- 1
- "1"
- "y"
- "yes"
- "t"
- "true"
- True
- "True"
- "active"
- "enabled"
- "on"

Values that evaluate as `False`, where quoted values are strings, and unquoted values are either boolean or integer.

- 0
- "0"
- "n"
- "no"
- "f"
- "false"
- False
- "False"
- "inactive"
- "disabled"
- "off"

Any other value will raise a `400 Bad Request` error.
