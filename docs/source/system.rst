.. _system:

System
======

The `@system` endpoint exposes system information about the Plone backend.

Send a GET request to the `@system` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/system_get.req

The response will contain the system information::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/@system",
    "cmf_version": "2.4.2",
    "debug_mode": "No",
    "pil_version": "6.2.1 (Pillow)",
    "plone_gs_metadata_version_file_system": "5208",
    "plone_gs_metadata_version_installed": "5208",
    "plone_version": "5.2.1",
    "python_version": "3.7.7 (default, Mar 10 2020, 15:43:33) \n[Clang 11.0.0 (clang-1100.0.33.17)]",
    "zope_version": "4.1.3"
  }


.. note:: The system endpoint is protected by the ``plone.app.controlpanel.Overview`` permission that requires the site-administrator or manager role.