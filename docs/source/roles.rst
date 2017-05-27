Roles
=====

Available roles in a Plone site can be queried by interacting with the ``/@roles`` endpoint on portal root (requires an authenticated user):

List Roles
----------

To retrieve a list of all roles in the portal, call the ``/@roles`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: _json/groups.req

The server will respond with a list of all groups in the portal:

.. literalinclude:: _json/roles.resp
   :language: http
