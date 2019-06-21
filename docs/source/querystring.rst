Querystring
===========

The ``@querystring`` endpoint returns the querystring config of ``plone.app.querystring``.

Instead of simply exposing the querystring related ``field`` and ``operation``
entries from the registry, it serializes them the same way the
``@@querybuilderjsonconfig`` view from p.a.querystring does.

This form is structured in a more conventient way for frontends to process:

- **Vocabularies** will be resolved, and their values will be inlined in the
  ``values`` property
- **Operations** will be inlined as well. The ``operations`` property will contain
  the list of operations (dotted names), and the ``operators`` property will
  contain the full definition of each of those operations supported by that field.
- Indexes that are flagged as **sortable** are listed in a dedicated top-level property
  ``sortable_indexes``

Available options for the querystring in a Plone site can be queried by interacting with the ``/@querystring`` endpoint on portal root:

Querystring Config
------------------

To retrieve all querystring options in the portal, call the ``/@querystring`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/querystring_get.req

The server will respond with all querystring options in the portal:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/querystring_get.resp
   :language: http
