.. _sharing:

Database
========

The `@database` endpoint exposes system information about the Plone database (ZODB).

Send a GET request to the `@database` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/database_get.req

The response will contain the database information:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/database_get.resp
   :language: http

.. note:: The system endpoint is protected by the ``plone.app.controlpanel.Overview`` permission that requires the site-administrator or manager role.