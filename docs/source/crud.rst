CRUD Web Services
=================

POST: /folder (Create a new document)
GET: /folder/{documentId} (Request the current state of the document)
PUT: /folder/{documentId} (Update the document)
DELETE: /folder/{documentId} (Remove the document


Creating a Resource with POST
-----------------------------

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

Successful Response::

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

Alternative if we know the id up-front: POST to /folder/my-document


Reading Resource State with GET
-------------------------------

Requesting a resource with GET::

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
Date:


Updating a Rescurce with PUT
----------------------------

Difference POST and PUT:

  * Use POST to create a resource identified by a service-generated URI
  * Use POST to append a resource to a collection identified by a service-generated URI
  * Use PUT to create or overwrite a resource

Updating a resource::

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

DELETE /folder/my-document HTTP/1.1
Host: localhost:8080

Successful response::

HTTP/1.1  204 No Content

Response:

  * 404 Resource does not exist
  * 405 Method not allowed
  *





