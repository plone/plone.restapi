.. _sharing:

System
======

The `@system` endpoint exposes system information about the Plone backend.

Send a GET request to the `@system` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/system_get.req

The response will contain the system information:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/system_get.resp
   :language: http

.. note:: The system endpoint is protected by the ``plone.app.controlpanel.Overview`` permission that requires the site-administrator or manager role.