.. include:: alert-noindex.rst

.. _error-handling:

Error handling
==============

Our API uses the full range of available HTTP codes to return meaningful information about errors. Each response might contain a JSON body detailing the error that occurred.

Exceptions
----------

In case the server encounters an error, if the authorization level is adequate (like it is done for error pages) then the client receives a full traceback::

  HTTP/1.1 500 Internal Server Error
  Content-Type: application/json
  {
    "@error": {
      "type": "AttributeError",
      "exception": "<Item at /foo> has no attribute 'bar'",
      "traceback": "..."
    }
  }

If the authorization level is not enough, the client receives just an error hash::

  HTTP/1.1 500 Internal Server Error
  Content-Type: application/json
  {
    "@error": {
      "hash": "..."
    }
  }


Malformed requests
------------------

If the request sent by the client contains errors related to the inputs provided (wrong querystring, wrong JSON body, missing pieces) the API will return a ``400 Bad Request``, with a descriptive text of the error::

  HTTP/1.1 400 Bad Request
  Content-Type: application/json
  {
    "@error": {
      ...
    }
  }
