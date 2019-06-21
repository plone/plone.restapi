Querystring
===========

Available options for the querystring in a Plone site can be queried by interacting with the ``/@querystring`` endpoint on portal root:

Querystring Options
-------------------

To retrieve all querystring options in the portal, call the ``/@querystring`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/querystring.req

The server will respond with all querystring options in the portal:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/querystring.resp
   :language: http
