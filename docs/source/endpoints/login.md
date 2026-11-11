---
myst:
  html_meta:
    "description": "The @login endpoint exposes the list of external authentication services that may be used in the Plone site."
    "property=og:description": "The @login endpoint exposes the list of external authentication services that may be used in the Plone site."
    "property=og:title": "@login for external authentication links"
    "keywords": "Plone, plone.restapi, REST, API, login, authentication, external services"
---

# Login for external authentication links

It is common to use add-ons that allow logging in to your site using third party services.
Such add-ons include using authentication services provided by KeyCloak, GitHub, or other OAuth2 or OpenID Connect enabled services.

When you install one of these add-ons, it modifies the login process, directing the user to third party services.

To expose the links provided by these add-ons, `plone.restapi` provides an adapter based service registration.
It lets those add-ons know that the REST API can use those services to authenticate users.
This will mostly be used by frontends that need to show the end user the links to those services.

To achieve that, third party products need to register one or more adapters for the Plone site root object, providing the `plone.restapi.interfaces.IExternalLoginProviders` interface.

In the adapter, the add-on needs to return the list of external links and some metadata, including the `id`, `title`, and name of the `plugin`.

An example adapter would be the following, in a file named {file}`adapter.py`:

```python
from zope.component import adapter
from zope.interface import implementer

@adapter(IPloneSiteRoot)
@implementer(IExternalLoginProviders)
class MyExternalLinks:
    def __init__(self, context):
        self.context = context

    def get_providers(self):
        return [
            {
                "id": "myprovider",
                "title": "Provider",
                "plugin": "pas.plugins.authomatic",
                "url": "https://some.example.com/login-url",
            },
            {
                "id": "github",
                "title": "GitHub",
                "plugin": "pas.plugins.authomatic",
                "url": "https://some.example.com/login-authomatic/github",
            },
        ]
```

With the corresponding ZCML stanza, in the corresponding {file}`configure.zcml` file:

```xml
<adapter factory=".adapter.MyExternalLinks" name="my-external-links"/>
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
