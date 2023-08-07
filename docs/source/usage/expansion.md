---
myst:
  html_meta:
    "description": "Expansion is a mechanism in plone.restapi to embed additional components—such as navigation, breadcrumbs, schema, or workflows—within the main content response. This helps the API consumers avoid unnecessary requests."
    "property=og:description": "Expansion is a mechanism in plone.restapi to embed additional components—such as navigation, breadcrumbs, schema, or workflows—within the main content response. This helps the API consumers avoid unnecessary requests."
    "property=og:title": "Expansion"
    "keywords": "Plone, plone.restapi, REST, API, Expansion"
---

(expansion-label)=

# Expansion

Expansion is a mechanism in `plone.restapi` to embed additional "components"—such as navigation, breadcrumbs, schema, or workflows—within the main content response.
This helps the API consumers avoid unnecessary requests.

Say you want to show a document in Plone together with the breadcrumbs and a workflow switcher.
Instead of doing three individual requests, you can expand the breadcrumbs and the workflow "components" within the document `GET` request.

The list of expandable components is listed in the `@components` attribute in the response of any content `GET` request:

```http
GET /plone/front-page HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

{
  "@id": "http://localhost:55001/plone/front-page",
  "@type": "Document",
  "@components": [
    {
      "@id": "http://localhost:55001/plone/front-page/@actions"
    },
    {
      "@id": "http://localhost:55001/plone/front-page/@breadcrumbs"
    },
    {
      "@id": "http://localhost:55001/plone/front-page/@navigation"
    },
    {
      "@id": "http://localhost:55001/plone/front-page/@types"
    },
    {
      "@id": "http://localhost:55001/plone/front-page/@workflow"
    },
    {
      "more components": "..."
    }
  ],
  "UID": "1f699ffa110e45afb1ba502f75f7ec33",
  "title": "Welcome to Plone",
  "more attributes": "..."
}
```

Request (unexpanded):

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/expansion.req
```

Response (unexpanded):

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/expansion.resp
:language: http
```

In order to expand and embed one or more components, use the `GET` parameter `expand`, and provide either a single component or a comma-separated list of the components you want to embed.
Say you want to expand the `breadcrumbs` component:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/expansion_expanded.req
```

Response (breadcrumbs expanded):

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/expansion_expanded.resp
:language: http
```

Here is an example of a request that expands all possible expansions:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/expansion_expanded_full.req
```

And the response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/expansion_expanded_full.resp
:language: http
```
