Indexes
=======

The ``/@indexes`` endpoint lists indexes that can be used to search a Plone site.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/indexes.req

    GET /plone/@indexes HTTP/1.1
    Accept: application/json
    Authorization: Basic YWRtaW46c2VjcmV0

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/indexes.resp
   :language: http

HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "name": "review_state",
    "group": "Metadata",
    "title": "Review state",
    "description": "An item's workflow state (e.g.published)",
    "type": "field",
    "visible": true,
    "vocabulary": "plone.app.vocabularies.WorkflowStates"
  }
]

Returned properties include:

name
  internal name of the index
type
  type of the index. for example:

  * text
  * field
  * keywords
  * boolean
  * date
  * uuid
  * daterange
  * daterecurring
  * path
  * gopip

title
  user-friendly title of the index
description
  user-friendly help about the index
group
  user-friendly group this index is included in
visible
  is this index visible for building queries?
vocabulary
  name of a vocabulary of index values that can be queried using the ``/@vocabularies`` endpoint.

** Implementation note: see plone.app.querystring.registryreader for how to get group, title, description, enabled (visible), and vocabulary from the registry. **
