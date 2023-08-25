---
myst:
  html_meta:
    "description": "Given a user in the site, one can get its properties and available fields."
    "property=og:description": "Given a user in the site, one can get its properties and available fields."
    "property=og:title": "User schema"
    "keywords": "Plone, plone.restapi, REST, API, Users, profile"
---

# User schema

```{note}
    This is only available on Plone 5.
```

Users in Plone have a set of properties defined by a default set of fields such as `fullname`, `email`, `portrait`, and so on.
These properties define the site user's profile and the user itself via the Plone UI, or the site managers can add them in a variety of ways including PAS plugins.

These fields are dynamic and customizable by integrators so they do not adhere to a fixed schema interface.
This dynamic schema is exposed by this endpoint in order to build the user's profile form.

## Getting the user schema

To get the current user schema, make a request to the `/@userschema` endpoint.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/userschema.req
```

The server will respond with the user schema.

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/userschema.resp
   :language: http
```

The user schema uses the same serialization as the type's JSON schema.

See {ref}`types-schema` for detailed documentation about the available field types.
