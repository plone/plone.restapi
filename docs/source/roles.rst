Roles
=====

Available roles in a Plone site can be queried by interacting with the ``/@roles`` endpoint on portal root (requires an authenticated user):

List Roles
----------

To retrieve a list of all roles in the portal, call the ``/@roles`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/roles.req

The server will respond with a list of all roles in the portal:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/roles.resp
   :language: http

The role ``title`` is the translated role title as displayed in Plone's
"Users and Groups" control panel.