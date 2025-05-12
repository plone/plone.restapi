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

## Site endpoint expanders

```{versionadded} plone.restapi 9.14.0

```

An add-on can add additional information to the `@site` endpoint by registering an `ISiteEndpointExpander` adapter.

For example, this adapter adds a key with a custom setting:

```python
from plone.restapi.interfaces import ISiteEndpointExpander
from zope.component import adapter
from zope.interface import implementer
from zope.interface import Interface
from myaddon.interfaces import IBrowserLayer

@adapter(Interface, IBrowserLayer)
@implementer(ISiteEndpointExpander)
class MyAddonExpander:

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, data):
        data["myaddon.setting"] = True
```

```{tip}
Use this for data that is needed to render any page, but that does not change depending on the context.
If the data is context-dependent, use a custom API expander instead.
```
