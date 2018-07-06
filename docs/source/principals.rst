Principals
==========

This endpoint will search for all the available principals in the local PAS
plugins given a query string. We call a principal to any user or group in the
system (requires an authenticated user):

Search Principals
-----------------

To retrieve a list of principals given a search string, call the ``/@principals`` endpoint with a GET request and a ``search`` query parameter:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/principals.req

The server will respond with a list of the users and groups in the portal that match the query string:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/principals.resp
   :language: http
