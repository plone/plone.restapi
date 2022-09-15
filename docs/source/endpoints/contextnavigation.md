---
myst:
  html_meta:
    "description": "The @contextnavigation endpoint uses the same semantics as the classic Plone navigation portlet. Instead of storing the portlet configuration in a portlet assignment storage, you can pass these as
parameters to the service or expand the component."
    "property=og:description": "The @contextnavigation endpoint uses the same semantics as the classic Plone navigation portlet. Instead of storing the portlet configuration in a portlet assignment storage, you can pass these as
parameters to the service or expand the component."
    "property=og:title": "Context Navigation"
    "keywords": "Plone, plone.restapi, REST, API, Context, Navigation"
---

(contextnavigation)=

# Context Navigation


## Top-Level Navigation

Get the top-level navigation items:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/contextnavigation.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/contextnavigation.resp
:language: http
```

The `@contextnavigation` endpoint uses the same semantics as the classic Plone navigation portlet, largely through reusing the same code.
Instead of storing the portlet configuration in a portlet assignment storage, you can pass these as
parameters to the service or expand the component.

You can provide these parameters:

- `name` - The title of the navigation tree.
- `root_path` - Root node path, can be "frontend path", derived from router
- `includeTop` - Bool. Include top nodeschema
- `currentFolderOnly` - Bool. Only show the contents of the current folder.
- `topLevel` - Int. Start level
- `bottomLevel` - Int. Navigation tree depth
- `no_icons` - Bool. Suppress Icons
- `thumb_scale` - String. Override thumb scale
- `no_thumbs` - Bool. Suppress thumbs

You should prefix these parameters with `expand.contextnavigation.`
A request would look like the following:

`http://localhost:55001/plone/?expand.contextnavigation.topLevel=1&expand.contextnavigation.name=Custom+name`
