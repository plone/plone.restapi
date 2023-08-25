---
myst:
  html_meta:
    "description": "Get the current state and history of an object, or workflow, by issuing a GET request for any context."
    "property=og:description": "Get the current state and history of an object, or workflow, by issuing a GET request for any context."
    "property=og:title": "Workflow"
    "keywords": "Plone, plone.restapi, REST, API, Workflow"
---

# Workflow

```{note}
Currently the workflow support is limited to executing transitions on content.
```

In Plone, content almost always has a {term}`workflow` attached.
We can get the current state and history of an object by issuing a `GET` request for any context:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflow_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflow_get.resp
:language: http
```

Now if we want to change the state of the front page to publish, we would proceed by issuing a `POST` request to the given URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflow_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflow_post.resp
:language: http
```

We can also change the state recursively for all contained items, provide a comment, and set effective and expiration dates:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workflow_post_with_body.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workflow_post_with_body.resp
:language: http
```
