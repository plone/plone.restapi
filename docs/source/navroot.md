---
html_meta:
  "description": "Navigation root is a concept that provides a way to root catalog queries, searches, and breadcrumbs in Plone."
  "property=og:description": "Navigation root is a concept that provides a way to root catalog queries, searches, and breadcrumbs in Plone."
  "property=og:title": "Navigation Root"
  "keywords": "Plone, plone.restapi, REST, API, site, navigation root"
---


## Navigation root

Plone has an idea called {term}`navigation root` which provides a way to root catalog queries, searches, breadcrumbs, etc. in a given section of the site.
This feature is useful when working with subsites or multilingual sites, because it allows the site manager to restrict searches or navigation queries to a specific location in the site.

This navigation root information is different depending on the context where is requested. For instance in a default multilingual site, when browsing the contents inside a language folder, the navigation root will be the language folder, but in a non-multilingual site the navigation root will be the root of the site.

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

In a multilingual site, where the language folder is the navigation root, the response has the language
folder information:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navroot_lang_folder_get.req
```

The response will contain the navigation root information with the site :

```{literalinclude} ../../src/plone/restapi/tests/http-examples/navroot_lang_folder_get.resp
:language: http
```

In a multilingual site if the navigation root is requested for a content inside a language folder, the response has the language folder information as a navigation root:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navroot_lang_content_get.req
```

The response will contain the navigation root information with the site :

```{literalinclude} ../../src/plone/restapi/tests/http-examples/navroot_lang_content_get.resp
:language: http
```

## Expansion

This endpoint can be used with the {doc}`expansion` mechanism which allows getting more information about a content item in one query, avoiding unnecessary requests.

If a simple `GET` request is done on the content item, a new entry will be shown on the `@components` entry, with the URL of the `@navroot` endpoint.
