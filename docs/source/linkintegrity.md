---
html_meta:
  "description": "Returns a list of possible reference breaches for given objects."
  "property=og:description": "Returns a list of possible reference breaches for given objects."
  "property=og:title": "Link integrity"
  "keywords": "Plone, plone.restapi, REST, API, Linkintegrity"
---

# Link integrity

When you create relations between contents in Plone (for example with relation fields or links in text), these relations are automatically stored in the database.
When you try to delete a content from Plone interface, you will get a warning if that content is referenced by one or more contents to avoid possible reference breaches.

If you are going to delete a folderish content, the check will be performed for all contents in that folder too.

The `@linkintegrity` endpoint returns the list of reference breaches.

You can call the `/@linkintegrity` endpoint on site root with a `GET` request and a list of uids in JSON BODY:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/linkintegrity_get.req

The server will respond with the results:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/linkintegrity_get.resp
   :language: http

The endpoint accepts only a parameter:

  - ``uids`` (a list of object uids that you want to check)
