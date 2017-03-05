Users
=====

Available users in a Plone site can be created, queried, updated and deleted by interacting with the ``/@users`` endpoint on portal root (requires an authenticated user):

List Users
----------

To retrieve a list of all current users in the portal, call the ``/@users`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: _json/users.req

The server will respond with a list of all users in the portal:

.. literalinclude:: _json/users.resp
   :language: http

The endpoint supports some basic filtering:

..  http:example:: curl httpie python-requests
    :request: _json/users_filtered_by_username.req

The server will respond with a list the filtered users in the portal with username starts with the query.

.. literalinclude:: _json/users_filtered_by_username.resp
   :language: http

The endpoint also takes a ``limit`` parameter that defaults to a maximum of 25 users at a time for performance reasons.


Create User
-----------

To create a new user, send a ``POST`` request to the global ``/@users`` endpoint with a JSON representation of the user you want to create in the body:

..  http:example:: curl httpie python-requests
    :request: _json/users_created.req


.. note::
    By default, "username", and "password" are required fields. If email login is enabled, "email" and "password" are required fields. All other fields in the example are optional.

If the user has been created successfully, the server will respond with a status 201 (Created). The ``Location`` header contains the URL of the newly created user and the resource representation in the payload:

.. literalinclude:: _json/users_created.resp
   :language: http


Read User
---------

To retrieve all details for a particular user, send a ``GET`` request to the ``/@users`` endpoint and append the user id to the URL:

..  http:example:: curl httpie python-requests
    :request: _json/users_get.req

The server will respond with a 200 OK status code and the JSON representation of the user in the body:

.. literalinclude:: _json/users_get.resp
   :language: http


Update User
-----------

To update the settings of a user, send a ``PATCH`` request with the user details you want to amend to the URL of that particular user, e.g. if you want to update the email address of the admin user to:

..  http:example:: curl httpie python-requests
    :request: _json/users_update.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/users_update.resp
   :language: http


Delete User
-----------

To delete a user send a ``DELETE`` request to the ``/@users`` endpoint and append the user id of the user you want to delete, e.g. to delete the user with the id johndoe:

..  http:example:: curl httpie python-requests
    :request: _json/users_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/users_delete.resp
   :language: js
