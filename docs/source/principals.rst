Principals
==========

This endpoint will search for all the available principals in the local PAS
plugins given a query string. We call a principal to any user or group in the
system (requires an authenticated user):

Search Principals
-----------------

To retrieve a list of principals given a search string, call the ``/@principals`` endpoint with a GET request and a ``search`` query parameter:

.. example-code::

  .. code-block:: http-request

    GET /@principals?search=ploneteam HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@principals?search=ploneteam

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@principals?search=ploneteam Accept:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@principals?search=ploneteam', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

The server will respond with a list of the users and groups in the portal that match the query string:

.. literalinclude:: _json/principals.json
   :language: js
