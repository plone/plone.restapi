---
html_meta:
  "description": "Returns a list of possible reference breaches for given objects."
  "property=og:description": "Returns a list of possible reference breaches for given objects."
  "property=og:title": "Link integrity"
  "keywords": "Plone, plone.restapi, REST, API, Linkintegrity"
---

# Link Integrity

When you create relations between content objects in Plone (e.g. via relation fields or links in text blocks), these relations are stored in the database.
The Plone user interface will use those stored relations to show a warning when you try to delete a content object that is still referenced somewhere.
This avoids broken links ("breaches") in the site.

This check includes content objects that are located within a content object ("folderish content").

The `@linkintegrity` endpoint returns the list of reference breaches. If there are none, it will return an empty list ("[]").

You can call the `/@linkintegrity` endpoint on site root with a `GET` request and a list of uids in JSON BODY:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/linkintegrity_get.req

The server will respond with the results:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/linkintegrity_get.resp
   :language: http

The endpoint accepts a single parameter:

  - ``uids`` (a list of object uids that you want to check)
