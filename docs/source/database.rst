.. _database:

Database
========

The `@database` endpoint exposes system information about the Plone database (ZODB).

Send a GET request to the `@database` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/database_get.req

The response will contain the database information::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/@database",
    "cache_detail_length": [
      {
        "connection": "<Connection at 11238e150>",
        "ngsize": 393,
        "size": 862
      },
      {
        "connection": "<Connection at 112530c50>",
        "ngsize": 46,
        "size": 261
      }
    ],
    "cache_length": 439,
    "cache_length_bytes": 0,
    "cache_size": 400,
    "database_size": 230,
    "db_name": "FunctionalTest",
    "db_size": 92516
  }

.. note:: The system endpoint is protected by the ``plone.app.controlpanel.Overview`` permission that requires the site-administrator or manager role.