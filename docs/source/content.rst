Content Manipulation
====================

plone.restapi does not only expose content objects via a RESTful API. The API consumer can create, read, update, and delete a content object. Those operations can be mapped to the HTTP verbs POST (Create), GET (Read), PUT (Update) and DELETE (Delete).

Manipulating resources across the network by using HTTP as an application protocol is one of core principles of the REST architectural pattern. This allows us to interact with a specific resource in a standardized way:

======= ======================= ==============================================
Verb    URL                     Action
======= ======================= ==============================================
POST    /folder                 Creates a new document within the folder
GET     /folder/{document-id}   Request the current state of the document
PATCH   /folder/{document-id}   Update the document details
DELETE  /folder/{document-id}   Remove the document
======= ======================= ==============================================


Creating a Resource with POST
-----------------------------

To create a new resource, we send a POST request to the resource container.
If we want to create a new document within an existing folder, we send a POST request to that folder:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_post.req

By setting the 'Accept' header, we tell the server that we would like to receive the response in the 'application/json' representation format.

The 'Content-Type' header indicates that the body uses the 'application/json' format.

The request body contains the minimal necessary information needed to create a document (the type and the title).
You could set other properties, like "description" here as well.


Successful Response (201 Created)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a resource has been created, the server responds with the :term:`201 Created` status code.
The 'Location' header contains the URL of the newly created resource and the resource representation in the payload:


.. literalinclude:: ../../src/plone/restapi/tests/http-examples/content_post.resp
   :language: http


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
[


Reading a Resource with GET
---------------------------

After a successful POST, we can access the resource by sending a GET request to the resource URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_get.req


Successful Response (200 OK)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a resource has been retrieved successfully, the server responds with :term:`200 OK`:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/content_get.resp
   :language: http


For folderish types, their childrens are automatically included in the response
as ``items``. To disable the inclusion, add the GET parameter ``include_items=false``
to the URL.

By default only basic metadata is included. To include additional metadata,
you can specify the names of the properties with the ``metadata_fields`` parameter.
See also :ref:`retrieving-additional-metadata`.

The following example additionaly retrieves the UID and Creator:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_get_folder.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/content_get_folder.resp
   :language: http

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

You can find implementation details in the `plone.restapi.services.content.add.FolderPost class <https://github.com/plone/plone.restapi/blob/dde57b88e0f1b5f5e9f04e6a21865bc0dde55b1c/src/plone/restapi/services/content/add.py#L35-L61>`_


GET Responses
^^^^^^^^^^^^^

Possible server reponses for a GET request are:

* :term:`200 OK`
* :term:`404 Not Found`
* :term:`500 Internal Server Error`


Updating a Resource with PATCH
------------------------------

To update an existing resource we send a PATCH request to the server.
PATCH allows to provide just a subset of the resource
(the values you actually want to change).

If you send the value ``null`` for a field, the field's content will be
deleted and the ``missing_value`` defined for the field in the schema
will be set. Note that this is not possible if the field is ``required``,
and it only works for Dexterity types, not Archetypes:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_patch.req


Successful Response (204 No Content)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response by default:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/content_patch.resp
   :language: http


Successful Response (200 OK)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can get the object representation by adding a `Prefer` header with a value of `return=representation` to the PATCH request.
In this case, the response will be a :term:`200 OK`:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_patch_representation.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/content_patch_representation.resp
   :language: http

See for full specs the `RFC 5789: PATCH Method for HTTP <http://tools.ietf.org/html/rfc5789>`_


Replacing a Resource with PUT
-----------------------------

.. note::

  PUT is not implemented yet.

To replace an existing resource we send a PUT request to the server:

TODO: Add example.

In accordance with the HTTP specification, a successful PUT will not create a new resource or produce a new URL.

PUT expects the entire resource representation to be supplied to the server, rather than just changes to the resource state.
This is usually not a problem since the consumer application requested the resource representation before a PUT anyways.

When the PUT request is accepted and processed by the service, the consumer will receive a :term:`204 No Content` response (:term:`200 OK` would be a valid alternative).


Successful Update (204 No Content)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

When a resource has been updated successfully, the server sends a :term:`204 No Content` response:

TODO: Add example.


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

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/content_delete.resp
   :language: http


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


Reordering sub resources
------------------------
The resources contained within a resource can be reordered using the `ordering` key using a PATCH request on the container.

Use the `obj_id` subkey to specify which resource to reorder.
The subkey `delta` can be 'top', 'bottom', or a negative or positive integer for moving up or down.

Reordering resources within a subset of resources can be done using the `subset_ids` subkey.

A response 400 BadRequest with a message 'Client/server ordering mismatch' will be returned if the value is not in the same order as serverside.

A response 400 BadRequest with a message 'Content ordering is not supported by this resource' will be returned if the container does not support ordering.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_reorder.req

To rearrange all items in a folderish context use the `sort` key.

The `on` subkey defines the catalog index to be sorted on. The `order` subkey indicates 'ascending' or 'descending' order of items.

A response 400 BadRequest with a message 'Content ordering is not supported by this resource' will be returned if the container does not support ordering.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/content_resort.req


