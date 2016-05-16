=================
CRUD Web Services
=================

CRUD is a pattern for manipulating resources across the network by using HTTP as an application protocol. The CRUD operations (Create, Read, Update, Delete) can be mapped to the corresponding HTTP verbs POST (Create), GET (Read), PUT (Update) and DELETE (Delete). This allows us to interact with a specific resource in a standardized way:

======= ======================= ==============================================
Verb    URL                     Action
======= ======================= ==============================================
POST    /folder                 Creates a new document within the folder
GET     /folder/{documentId}    Request the current state of the document
PUT     /folder/{documentId}    Update the document details
DELETE  /folder/{documentId}    Remove the document
======= ======================= ==============================================


Creating a Resource with POST
=============================

To create a new resource, we send a POST request to the resource container.  If we want to create a new document within an existing folder, we send a POST request to that folder::

  POST /folder HTTP/1.1
  Host: localhost:8080
  Accept: application/json
  Content-Type: application/json

  {
      '@type': 'Document',
      'title': 'My Document',
  }

By setting the 'Accept' header, we tell the server that we would like to recieve the response in the 'application/json' representation format.

The 'Content-Type' header indicates that the body uses the 'application/json' format.

The request body contains the necessary information that is needed to create a document (the type and the title).


Successful Response (201 Created)
---------------------------------

If a resource has been created, the server responds with the '201 Created' status code. The 'Location' header contains the URL of the newly created resource and the resource represenation in the payload::

  HTTP/1.1 201 Created
  Content-Type: application/json
  Location: http://localhost:8080/folder/my-document

  {
      '@type': 'Document',
      'id': 'my-document',
      'title': 'My Document',
  }

Unsuccessful Response (400 Bad Request)
---------------------------------------

If the resource could not be created, for instance because the title was missing in the request, the server responds with '400 Bad Request'::

  HTTP/1.1 400 Bad Request
  Content-Type: application/json

  {
    'message': 'Required title field is missing'
  }

The response body can contain information about why the request failed.


Unsuccessful Response (500 Internal Server Error)
-------------------------------------------------

If the server can not properly process a request, it responds with '500 Internal Server Error'::

  HTTP/1.1 500 Internal Server Error
  Content-Type: application/json

  {
    'message': 'Internal Server Error'
  }

The response body can contain further information such as an error trace or a link to the documentation.


Possible POST Responses
-----------------------

Possible server reponses for a POST request are:

* :ref:`201 Created` (Resource has been created successfully)
* :ref:`400 Bad Request` (malformed request to the service)
* :ref:`500 Internal Server Error` (server fault, can not recover internally)


POST Implementation
-------------------

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
===========================

After a successful POST, we can access the resource by sending a GET request to the resource URL::

  GET /folder/my-document HTTP/1.1
  Host: localhost:8080
  Accept: application/json


Successful Response (200 OK)
----------------------------

If a resource has been retrieved successfully, the server responds with '200 OK':

.. literalinclude:: _json/document.json
   :language: js


Unsuccessful response (404 Not Found)
-------------------------------------

If a resource could not be found, the server will respond with '404 Not Found'::

  HTTP/1.1 404 Not Found
  Content-Type: application/json

  {
    'error': 'NotFound'
  }


GET Implementation
------------------

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
-------------

Possible server reponses for a GET request are:

* :ref:`200 OK`
* :ref:`404 Not Found`
* :ref:`500 Internal Server Error`


Updating a Resource with PUT
============================

To update an existing resource we send a PUT request to the server::

  PUT /folder/my-document HTTP/1.1
  Host: localhost:8080
  Content-Type: application/json

  {
      '@type': 'Document',
      'title': 'My New Document Title',
  }

In accordance with the HTTP specification, a successful PUT will not create a new resource or produce a new URL.

PUT expects the entire resource representation to be supplied to the server, rather than just changes to the resource state. This is usually not a problem since the consumer application requested the resource representation before a PUT anyways.

An alternative is to use the PATCH HTTP verb, that allows to provide just a subset of the resource. We do not implement PATCH for now though.

When the PUT request is accepted and processed by the service, the consumer will receive either a 200 OK response or a 204 No Content response.


Successful Update (200 OK)
--------------------------

When a resource has been updated successfully, the server sends a '200 OK' response::

  HTTP/1.1 200 OK
  Content-Type:: application/json

  {
      '@type': 'Document',
      'title': 'My New Document',
  }

An alternative would be to return a '204 No Content' response. This is more efficent since it does not contain a body. We choose do use '200 OK' for now though.

Unsuccessful Update (409 Conflict)
----------------------------------

Sometimes requests fail due to incompatible changes. The response body should include additional information about the problem.

TODO: We need to check if we can find a valid example for this in Plone.

PUT Implementation
------------------

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
-------------

Possible server reponses for a PUT request are:

* :ref:`200 OK`
* :ref:`404 Not Found`
* :ref:`409 Conflict`
* :ref:`500 Internal Server Error`


POST vs. PUT
------------

Difference POST and PUT:

  * Use POST to create a resource identified by a service-generated URI
  * Use POST to append a resource to a collection identified by a service-generated URI
  * Use PUT to overwrite a resource


Removing a Resource with DELETE
===============================

We can delete an existing resource by sending a DELETE request::

  DELETE /folder/my-document HTTP/1.1
  Host: localhost:8080

A successful response will be indicated by a '204 No Content' response::

  HTTP/1.1  204 No Content


DELETE Implementation
---------------------

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
----------------

Possible responses to a delete request are:

  * :ref:`204 No Content`
  * :ref:`404 Not Found` (if the resource does not exist)
  * :ref:`405 Not Allowed` (if deleting the resource is not allowed)
  * :ref:`500 Internal Server Error`
