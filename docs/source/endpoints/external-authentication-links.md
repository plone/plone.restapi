---
myst:
  html_meta:
    "description": "The @login endpoint exposes the list of external authentication services that may be used in the Plone site."
    "property=og:description": "The @login endpoint exposes the list of external authentication services that may be used in the Plone site."
    "property=og:title": 'External authentication links"
    "keywords": 'Plone, plone.restapi, REST, API, Login, Authentication, External services"
---

# External authentication links

It is common to have third party addons that allow logging in in your site using third party services.

Such addons include using KeyCloak, GitHub or other OAuth2 or OpenID Connect enabled services.

In such cases, an addon is installed in Plone and those addons modify the way that the login works, in order to direct to user to those third party services.

To expose the links provided by those addons, plone.restapi provides an adapter based service registration, to let those addons know this REST API that those services could be used to authenticate users.

This will be mostly used by frontends, that need to show the end user the links to those services.

To achieve that, third party products need to register one or more adapters for the Plone site root object, providing the `plone.restapi.interfaces.IExternalLoginProviders` interface.

In such adapter, the addon need to return the list of external links and some metadata like the id, title and plugin name.

An example adapter would be the following (in an `adapter.py` file):

```python
from zope.component import adapts
from zope.interface import implementer

@adapts(IPloneSiteRoot)
@implementer(IExternalLoginProviders)
class MyExternalLinks:
    def get_providers(self):
        return [
            {
                "id": "myprovider",
                "title": "Provider",
                "plugin": "myprovider",
                "url": "https://some.example.com/login-url",
            },
            {
                "id": "github",
                "title": "GitHub",
                "plugin": "github",
                "url": "https://some.example.com/login-authomatic/github",
            },
        ]
```

With the corresponding ZCML stanza (in the corresponding `configure.zcml` file):

```xml
<adapter factory=".adapter.MyExternalLinks" />
```

The API request would be as follows:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/external_authentication_links.req
```

The server will respond with a `Status 200` and the list of external providers:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/external_authentication_links.resp
:language: http
```
