---
html_meta:
  "description": "Site endpoint for Plone REST API"
  "property=og:title": "Site endpoint for Plone REST API"
  "property=og:description": "Site endpoint for Plone REST API"
  "keywords": "Plone, plone.restapi, REST, API, site, navigation root"
---

# Site

The `@site` endpoint provides site-wide information, such as the site title, logo, and other information, which is useful to offer generic information about the Plone site.

Send a `GET` request to the `@site` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/site_get.req
```

The response will contain the site information:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/site_get.resp
:language: http
```

## Navigation root

Plone has an idea called `Navigation Root` which provides a way to root catalog queries, searches, breadcrumbs, etc. in a given section of the site. This feature is useful when working with subsites or multilingual sites, because allows the site manager to somehow restrict where the searches or navigation queries start on the site.

This navigation root information is different depending on the context where it is requested. For instance in a default multilingual site, when browsing the contents inside a language folder, the navigation root will be the language folder, but in a non-multilingual site the navigation root will be the root of the site.

To get the information about the navigation root, the REST API has a `@navroot` contextual endpoint, which will return the correct information about it.

For instance, send a `GET` request to the `@navroot` endpoint in the root of the site:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navroot_site_get.req
```

The response will contain the navigation root information with the site :

```{literalinclude} ../../src/plone/restapi/tests/http-examples/navroot_site_get.resp
:language: http
```

In a multilingual site, where the language folder is the navigation root, the response contains the language
folder information:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navroot_lang_folder_get.req
```

The response will contain the navigation root information with the site :

```{literalinclude} ../../src/plone/restapi/tests/http-examples/navroot_lang_folder_get.resp
:language: http
```

In a multilingual site if the navigation root is requested for a content inside a language folder, the response contains the language folder information as a navigation root:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navroot_lang_content_get.req
```

The response will contain the navigation root information with the site :

```{literalinclude} ../../src/plone/restapi/tests/http-examples/navroot_lang_content_get.resp
:language: http
```
