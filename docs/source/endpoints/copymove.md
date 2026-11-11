---
myst:
  html_meta:
    "description": "To copy a content object, use the /@copy endpoint at the destination's URL with the source object specified in the request body. Similarly use the /@move endpoint to move an object."
    "property=og:description": "To copy a content object, use the /@copy endpoint at the destination's URL with the source object specified in the request body. Similarly use the /@move endpoint to move an object."
    "property=og:title": "Copy and Move"
    "keywords": "Plone, plone.restapi, REST, API, Copy, Move"
---

# Copy and Move


## Copying an object

To copy a content object, send a `POST` request to the `/@copy` endpoint at the destination's URL with the source object specified in the request body.
The source object can be specified either by URL, path, UID or `intid`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/copy.req
```

If the copy operation succeeds, the server will respond with status {term}`200 OK`, and return the new and old URL of the copied object:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/copy.resp
:language: http
```


## Moving an object

To move a content object, send a `POST` request to the `/@move` endpoint at the destination's URL with the source object specified in the request body.
The source object can be specified either by URL, path, UID or `intid`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/move.req
```

If the move operation succeeds, the server will respond with status {term}`200 OK`, and return the new and old URL of the moved object:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/move.resp
:language: http
```


## Copying or moving multiple objects

Multiple objects can be moved or copied by giving a list of sources:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/copy_multiple.req
```

If the operation succeeds, the server will respond with status {term}`200 OK`, and return the new and old URLs for each copied or moved object:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/copy_multiple.resp
:language: http
```
