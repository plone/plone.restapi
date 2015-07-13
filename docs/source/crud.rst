CRUD Web Services
=================

CRUD (Create, Read, Update, Delete) is a pattern for manipulating resources across the network by using HTTP as an application protocol by mapping the CRUD operations to the corresponding HTTP verbs POST, GET, PUT and DELETE:


======= ======================= ==============================================
Verb    URL                     Action
======= ======================= ==============================================
POST    /folder                 Creates a new document with the folder
GET     /folder/{documentId}    Request the current state of the document
PUT     /folder/{documentId}    Update the document details
DELETE  /folder/{documentId}    Remove the document
======= ======================= ==============================================


Creating a Resource with POST
-----------------------------

Request::

  POST /folder HTTP/1.1
  Host: localhost:8080
  Content-Type: application/json
  Content-Length: 239

  {
      '@context': '/@@context.jsonld',
      '@type': 'Document',
      'title': 'My Document',
  }

Possible Responses:

* 201 Created (location header containing the newly created resource URL)
* 400 Bad Request (malformed request to the service)
* 500 Internal Server Error (server fault, can not recover internally)

Successful Response (201 Created)::

  HTTP/1.1 201 Created
  Content-Length: 267
  Content-Type: application/json
  Date:
  Location: http://localhost:8080/folder/my-document

  {
      '@context': '/@@context.jsonld',
      '@type': 'Document',
      'id': 'my-document',
      'title': 'My Document',
  }

Unsuccessful Response (400 Bad Request)::

  HTTP/1.1 400 Bad Request
  Content-Length: 250
  Content-Type: application/json

  {
    'message': 'Required title field is missing'
  }

Unsuccessful Response (500 Internal Server Error)::

  HTTP/1.1 500 Internal Server Error
  Content-Length: 250
  Content-Type: application/json

  {
    'message': 'Internal Server Error'
  }


POST Implementation (Pseudo Code Example)::

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


Reading Resource State with GET
-------------------------------

Request::

  GET /folder/my-document HTTP/1.1
  Host: localhost:8080

Response::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
      '@context': '/@@context.jsonld',
      '@type': 'Document',
      'id': 'my-document',
      'title': 'My Document',
  }

Unsuccessful response::

  HTTP/1.1 404 Not Found
  Content-Type: application/json

  {
    'error': 'NotFound'
  }


Updating a Rescurce with PUT
----------------------------

Difference POST and PUT:

  * Use POST to create a resource identified by a service-generated URI
  * Use POST to append a resource to a collection identified by a service-generated URI
  * Use PUT to create or overwrite a resource

Request::

  PUT: /folder/my-document HTTP/1.1
  Host: localhost:8080
  Content-Type: application/xml

  {
      '@context': '/@@context.jsonld',
      '@type': 'Document',
      'title': 'My New Document',
  }

In accordance with the HTTP specification, a successful PUT will not create a new resource or produce a new URL.

PUT expects the entire resource representation to be supplied to the server, rather than just changes to the resource state. This is usually not a problem since the consumer application requested the resource representation before a PUT anyways.

An alternative is to use the PATCH HTTP verb, that allows to provide just a subset of the resource. We do not implement PATCH for now though.

When the PUT request is accepted and processed by the service, the consumer will receive either a 200 OK response or a 204 No Content response.

Successful Update with 200 Response::

  HTTP/1.1 200 OK

  {
      '@context': '/@@context.jsonld',
      '@type': 'Document',
      'title': 'My New Document',
  }

An alternative would be to return a '204 No Content' response. This is more efficent since it does not contain a body.


Removing a Resource with DELETE
-------------------------------

Request::

  DELETE /folder/my-document HTTP/1.1
  Host: localhost:8080

Successful response::

  HTTP/1.1  204 No Content

Response:

  * 404 Resource does not exist
  * 405 Method not allowed
  *





