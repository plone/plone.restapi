CRUD Web Services
=================

CRUD is a pattern for manipulating resources across the network by using HTTP as an application protocol.
The CRUD operations (Create, Read, Update, Delete) can be mapped to the corresponding HTTP verbs POST (Create), GET (Read), PUT (Update) and DELETE (Delete).
This allows us to interact with a specific resource in a standardized way:

======= ======================= ==============================================
Verb    URL                     Action
======= ======================= ==============================================
POST    /folder                 Creates a new document within the folder
GET     /folder/{documentId}    Request the current state of the document
PUT     /folder/{documentId}    Update the document details
DELETE  /folder/{documentId}    Remove the document
======= ======================= ==============================================


Creating a Resource with POST
-----------------------------

To create a new resource, we send a POST request to the resource container.
If we want to create a new document within an existing folder, we send a POST request to that folder:

.. example-code::

  .. code-block:: http-request

    POST /folder HTTP/1.1
    Host: localhost:8080
    Accept: application/json
    Content-Type: application/json

    {
        '@type': 'Document',
        'title': 'My Document',
    }

  .. code-block:: curl

    curl -i -H "Accept: application/json" -H "Content-type: application/json" --data-raw '{"@type":"Document", "title": "My Document"}' --user admin:admin -X POST http://localhost:8080/Plone/folder

  .. code-block:: httpie

    http -a admin:admin POST http://localhost:8080/Plone/folder \\@type=Document title=My Document Accept:application/json

    .. code-block:: python-requests

      requests.post('http://localhost:8080/Plone/folder', auth=('admin', 'admin'), headers={'Accept': 'application/json'}, params={'@type': 'Document'})

By setting the 'Accept' header, we tell the server that we would like to receive the response in the 'application/json' representation format.

The 'Content-Type' header indicates that the body uses the 'application/json' format.

The request body contains the minimal necessary information needed to create a document (the type and the title).
You could set other properties, like "description" here as well.


Successful Response (201 Created)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a resource has been created, the server responds with the :term:`201 Created` status code.
The 'Location' header contains the URL of the newly created resource and the resource represenation in the payload::

  HTTP/1.1 201 Created
  Content-Type: application/json
  Location: http://localhost:8080/folder/my-document

  {
      '@type': 'Document',
      'id': 'my-document',
      'title': 'My Document',
  }

Unsuccessful Response (400 Bad Request)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the resource could not be created, for instance because the title was missing in the request, the server responds with :term:`400 Bad Request`::

  HTTP/1.1 400 Bad Request
  Content-Type: application/json

  {
    'message': 'Required title field is missing'
  }

The response body can contain information about why the request failed.


Unsuccessful Response (500 Internal Server Error)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If the server can not properly process a request, it responds with :term:`500 Internal Server Error`::

  HTTP/1.1 500 Internal Server Error
  Content-Type: application/json

  {
    'message': 'Internal Server Error'
  }

The response body can contain further information such as an error trace or a link to the documentation.


Possible POST Responses
^^^^^^^^^^^^^^^^^^^^^^^

Possible server reponses for a POST request are:

* :term:`201 Created` (Resource has been created successfully)
* :term:`400 Bad Request` (malformed request to the service)
* :term:`500 Internal Server Error` (server fault, can not recover internally)


POST Implementation
^^^^^^^^^^^^^^^^^^^

A pseudo-code example of the POST implementation on the server::

    try:
        order = createOrder()
        if order == None:
            # Bad Request
            response.setStatus(400)
        else:
            # Created
            response.setStatus(201)
    except:
        # Internal Server Error
        response.setStatus(500)

TODO: Link to the real implementation...


Reading a Resource with GET
---------------------------

After a successful POST, we can access the resource by sending a GET request to the resource URL:

.. example-code::

  .. code-block:: http-request

    GET /folder/my-document HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/folder/my-document

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/folder/my-document Accept:application/json

  .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/folder/my-document', auth=('admin', 'admin'), headers={'Accept': 'application/json'})


Successful Response (200 OK)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a resource has been retrieved successfully, the server responds with :term:`200 OK`:

.. literalinclude:: _json/document.json
   :language: js

.. note::
        For folderish types, collections or search results, the results will
        be **batched** if the size of the resultset exceeds the batch size.
        See :doc:`/batching` for more details on how to work with batched
        results.

Unsuccessful response (404 Not Found)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a resource could not be found, the server will respond with :term:`404 Not Found`::

  HTTP/1.1 404 Not Found
  Content-Type: application/json

  {
    'error': 'NotFound'
  }


GET Implementation
^^^^^^^^^^^^^^^^^^

A pseudo-code example of the GET implementation on the server::

    try:
        order = getOrder()
        if order == None:
            # Not Found
            response.setStatus(404)
        else:
            # OK
            response.setStatus(200)
    except:
        # Internal Server Error
        response.setStatus(500)

TODO: Link to the real implementation...


GET Responses
^^^^^^^^^^^^^

Possible server reponses for a GET request are:

* :term:`200 OK`
* :term:`404 Not Found`
* :term:`500 Internal Server Error`


Updating a Resource with PATCH
------------------------------

To update an existing resource we send a PATCH request to the server.
PATCH allows to provide just a subset of the resource (the values you actually want to change):

.. example-code::

  .. code-block:: http-request

    PATCH /folder/my-document HTTP/1.1
    Host: localhost:8080/Plone
    Content-Type: application/json

    {
        '@type': 'Document',
        'title': 'My New Document Title',
    }

  .. code-block:: curl

    curl -i -H "Accept: application/json" -H "Content-type: application/json" --data-raw '{title": "My Document"}' --user admin:admin -X PATCH http://localhost:8080/Plone/folder/my-document

  .. code-block:: httpie

    http -a admin:admin PATCH http://localhost:8080/Plone/folder/my-document title="My New Document Title" Accept:application/json

  .. code-block:: python-requests

    requests.patch('http://localhost:8080/Plone/folder/my-document', auth=('admin', 'admin'), headers={'Accept': 'application/json'}, data={'title': 'My New Document Title'})


Successful Response (204 No Content)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response::

  HTTP/1.1  204 No Content



See for full specs the `RFC 5789: PATCH Method for HTTP <http://tools.ietf.org/html/rfc5789>`_


Replacing a Resource with PUT
-----------------------------

.. note::

  PUT is not implemented yet.

To replace an existing resource we send a PUT request to the server:

.. example-code::

  .. code-block:: http-request

    PUT /folder/my-document HTTP/1.1
    Host: localhost:8080
    Content-Type: application/json

    {
        '@type': 'Document',
        'title': 'My New Document Title',
    }

  .. code-block:: curl

    curl -i -H "Accept: application/json" -X PUT http://localhost:8080/Plone/folder

  .. code-block:: httpie

    http -a admin:admin PUT http://localhost:8080/Plone/folder title="My New Document Title" Accept:application/json

  .. code-block:: python-requests

    requests.put('http://localhost:8080/Plone/folder/my-document', auth=('admin', 'admin'), headers={'Accept': 'application/json'}, data={'title': 'My New Document Title', ...})

In accordance with the HTTP specification, a successful PUT will not create a new resource or produce a new URL.

PUT expects the entire resource representation to be supplied to the server, rather than just changes to the resource state.
This is usually not a problem since the consumer application requested the resource representation before a PUT anyways.

When the PUT request is accepted and processed by the service, the consumer will receive a :term:`204 No Content` response (:term:`200 OK` would be a valid alternative).


Successful Update (204 No Content)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a resource has been updated successfully, the server sends a :term:`204 No Content` response::

  HTTP/1.1 204 No Content
  Content-Type:: application/json


Unsuccessful Update (409 Conflict)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes requests fail due to incompatible changes.
The response body includes additional information about the problem.

TODO: Add example.


PUT Implementation
^^^^^^^^^^^^^^^^^^

A pseudo-code example of the PUT implementation on the server::

    try:
        order = getOrder()
        if order:
            try:
                saveOrder()
            except conflict:
                response.setStatus(409)
            # OK
            response.setStatus(200)
        else:
            # Not Found
            response.setStatus(404)
    except:
        # Internal Server Error
        response.setStatus(500)

TODO: Link to the real implementation...


PUT Responses
^^^^^^^^^^^^^

Possible server reponses for a PUT request are:

* :term:`200 OK`
* :term:`404 Not Found`
* :term:`409 Conflict`
* :term:`500 Internal Server Error`


POST vs. PUT
^^^^^^^^^^^^

Difference between POST and PUT:

  * Use POST to create a resource identified by a service-generated URI
  * Use POST to append a resource to a collection identified by a service-generated URI
  * Use PUT to overwrite a resource

This follows `RFC 7231: HTTP 1.1: PUT Method <https://tools.ietf.org/html/rfc7231#section-4.3.4>`_.


Removing a Resource with DELETE
-------------------------------

We can delete an existing resource by sending a DELETE request:

.. example-code::

  .. code-block:: http-request

    DELETE /folder/my-document HTTP/1.1
    Host: localhost:8080

  .. code-block:: curl

      curl -i -H "Accept: application/json" -X DELETE --user admin:admin http://localhost:8080/Plone/folder/my-document

  .. code-block:: httpie

      http -a admin:admin DELETE http://localhost:8080/Plone/folder/my-document Accept:application/json

  .. code-block:: python-requests

    requests.delete('http://localhost:8080/Plone/folder', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

A successful response will be indicated by a :term:`204 No Content` response::

  HTTP/1.1  204 No Content


DELETE Implementation
^^^^^^^^^^^^^^^^^^^^^

A pseudo-code example of the DELETE implementation on the server::

    try:
        order = getOrder()
        if order:
            if can_delete(order):
                # No Content
                response.setStatus(204)
            else:
                # Not Allowed
                response.setStatus(405)
        else:
            # Not Found
            response.setStatus(404)
    except:
        # Internal Server Error
        response.setStatus(500)

TODO: Link to the real implementation...


DELETE Responses
^^^^^^^^^^^^^^^^

Possible responses to a delete request are:

  * :term:`204 No Content`
  * :term:`404 Not Found` (if the resource does not exist)
  * :term:`405 Method Not Allowed` (if deleting the resource is not allowed)
  * :term:`500 Internal Server Error`
