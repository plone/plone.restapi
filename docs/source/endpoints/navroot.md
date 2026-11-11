---
myst:
  html_meta:
    "description": "Navigation root is a concept that provides a way to root catalog queries, searches, and breadcrumbs in Plone."
    "property=og:description": "Navigation root is a concept that provides a way to root catalog queries, searches, and breadcrumbs in Plone."
    "property=og:title": "Navigation Root"
    "keywords": "Plone, plone.restapi, REST, API, site, navigation root"
---

(navigation-root-label)=

# Navigation root

Plone has a concept called {term}`navigation root` which provides a way to root catalog queries, searches, breadcrumbs, and so on in a given section of the site.
This feature is useful when working with subsites or multilingual sites, because it allows the site manager to restrict searches or navigation queries to a specific location in the site.

This navigation root information is different depending on the context of the request.
For instance, in a default multilingual site when browsing the contents inside a language folder such as `www.domain.com/en`, the context is `en` and its navigation root will be `/en/`.
In a non-multilingual site, the context is the root of the site such as `www.domain.com` and the navigation root will be `/`.

To get the information about the navigation root, the REST API has a `@navroot` contextual endpoint.
For instance, send a `GET` request to the `@navroot` endpoint at the root of the site:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_get.req
```

The response will contain the navigation root information for the site:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_get.resp
:language: http
```

If you request the `@navroot` of a given content item in the site:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_content_get.req
```

The response will contain the navigation root information in the context of that content item:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_content_get.resp
:language: http
```

In a multilingual site, the root of the site will work as usual:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_site_get.req
```

The response will contain the navigation root information of the root of the site:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_site_get.resp
:language: http
```

In a multilingual site where the language folder is the navigation root, the response has the language folder information:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_lang_folder_get.req
```

The response will contain the navigation root information for the language folder:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_lang_folder_get.resp
:language: http
```

In a multilingual site, if the navigation root is requested for content inside a language folder:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_lang_content_get.req
```

The response has the language folder information as a navigation root:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_lang_content_get.resp
:language: http
```

(navigation-root-expansion-label)=

## Expansion

This endpoint can be used with the {doc}`../usage/expansion` mechanism which allows getting more information about a content item in one query, avoiding unnecessary requests.

If a simple `GET` request is made on the content item, a new entry will be shown on the `@components` entry with the URL of the `@navroot` endpoint.

In a standard site when querying the site root:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_get_expansion.req
```

The response will contain information of the site root with the navigation expanded:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_get_expansion.resp
:language: http
```

When querying a content item inside the root:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_content_get_expansion.req
```

The response will contain the information of that content item with its navigation root information expanded:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/navroot_standard_site_content_get_expansion.resp
:language: http
```

In a multilingual site, it works the same.
Use the request:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/site_get_expand_navroot.req
```

And the response will contain the navigation root information pointing to the root of the site:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/site_get_expand_navroot.resp
:language: http
```

It will also work with language root folders that are navigation roots:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/site_get_expand_lang_folder.req
```

The response will contain the navigation root information expanded:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/site_get_expand_lang_folder.resp
:language: http
```

And also for content inside the language root folders:

```{eval-rst}
.. http:example:: curl httpie python-requests
   :request: ../../../src/plone/restapi/tests/http-examples/site_get_expand_lang_folder_content.req
```

The response will include the expanded information pointing to the language root:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/site_get_expand_lang_folder_content.resp
:language: http
```
