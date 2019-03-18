Users
=====

Available users in a Plone site can be created, queried, updated and deleted by interacting with the ``/@users`` endpoint on portal root (requires an authenticated user):

List Users
----------

To retrieve a list of all current users in the portal, call the ``/@users`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users.req

The server will respond with a list of all users in the portal:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users.resp
   :language: http


This only works for Manager users, anonymous users or logged-in users without Manager rights are now allowed to list users. This is the example as an anonymous user:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_anonymous.req

The server will return a 401 Unauthorized status code

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_anonymous.resp
   :language: http


And this one as an user without the proper rights:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_unauthorized.req

The server will return a 401 Unauthorized status code

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_unauthorized.resp
   :language: http


The endpoint supports some basic filtering:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_filtered_by_username.req

The server will respond with a list the filtered users in the portal with username starts with the query.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_filtered_by_username.resp
   :language: http

The endpoint also takes a ``limit`` parameter that defaults to a maximum of 25 users at a time for performance reasons.


Create User
-----------

To create a new user, send a ``POST`` request to the global ``/@users`` endpoint with a JSON representation of the user you want to create in the body:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_created.req


.. note::
    By default, "username", and "password" are required fields. If email login is enabled, "email" and "password" are required fields. All other fields in the example are optional.

    The field "username" is **not allowed** when email login is *enabled*.

If the user has been created successfully, the server will respond with a status 201 (Created). The ``Location`` header contains the URL of the newly created user and the resource representation in the payload:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_created.resp
   :language: http

If no roles has been specified, then a default ``Member`` role is added as a sensible default.


Read User
---------

To retrieve all details for a particular user, send a ``GET`` request to the ``/@users`` endpoint and append the user id to the URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_get.req

The server will respond with a 200 OK status code and the JSON representation of the user in the body:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_get.resp
   :language: http

The key 'roles' lists the globally defined roles for the user.

Only users with Manager rights are allowed to get other users' information:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_unauthorized_get.req

If the user lacks this rights, the server will respond with a 401 Unauthorized status code:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_unauthorized_get.resp
   :language: http

Also anonymous users are not allowed to get users' information:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_anonymous_get.req

If the user is an anonymous one, the server will respond with a 401 Unauthorized status code:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_anonymous_get.resp
   :language: http

But each user is allowed to get its own information.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_authorized_get.req

In this case, the server will respond with a 200 OK status code and the JSON respresentation of the user in the body:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_authorized_get.resp
   :language: http

Update User
-----------

To update the settings of a user, send a ``PATCH`` request with the user details you want to amend to the URL of that particular user, e.g. if you want to update the email address of the admin user to:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_update.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_update.resp
   :language: http

.. note::
  The 'roles' object is a mapping of a role and a boolean indicating adding or removing.

Any user is able to update their own properties and password (if allowed) by using the same request.

The user portrait/avatar can also be updated using the same serialization as the file one:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_update_portrait.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response.
Then asking for the user the portrait URL should be on the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_update_portrait_get.resp
   :language: http

Adding the portrait via the @user endpoint does not scale it since it's assumed that the frontend will take care of it (resizing/cropping).
If you still want that Plone to take care of the scaling using the default Plone behavior for portraits, you have to add the ``scale`` attribute to the request:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_update_portrait_scale.req

Delete User
-----------

To delete a user send a ``DELETE`` request to the ``/@users`` endpoint and append the user id of the user you want to delete, e.g. to delete the user with the id johndoe:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/users_delete.resp
   :language: http


User registration
-----------------

Plone allows you to enable the auto registration of users.
If it is enabled, then an anonymous user can register a new user using the user creation endpoint.
This new user will have the role ``Member`` by default as the Plone registration process also does.

To create a new user send a POST request to the '@users' endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_add.req

If the user should receive an email to set her password, you should pass 'sendPasswordReset": true' in the JSON body of the request.
Keep in mind that Plone will send a URL that points to the URL of the Plone site, which might just be your API endpoint.

If the user has been created, the server will respond with a :term:`201 Created` response:

..  literalinclude:: ../../src/plone/restapi/tests/http-examples/users_add.resp
    :language: http


Reset User Password
-------------------

Plone allows to reset a password for a user by sending a POST request to the user resource and appending `/reset-password` to the URL::

  POST /plone/@users/noam/reset-password HTTP/1.1
  Host: localhost:8080
  Accept: application/json

The server will respond with a :term:`200 OK` response and send an email to the user to reset her password.

The token that is part of the reset url in the email can be used to
authorize setting a new password:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/users_reset.req


Reset Own Password
^^^^^^^^^^^^^^^^^^

Plone also allows a user to reset her own password directly without sending an email. The endpoint and the request is the same as above, but now the user can send the old password and the new password as payload::

  POST /plone/@users/noam/reset-password HTTP/1.1
  Host: localhost:8080
  Accept: application/json
  Content-Type: application/json

  {
    'old_password': 'secret',
    'new_password': 'verysecret',
  }

The server will respond with a :term:`200 OK` response without sending an email.

To set the password with the old password you need either the ``Set own password`` or the ``plone.app.controlpanel.UsersAndGroups`` permission.

If an API consumer tries to send a password in the payload that is not the same as the currently logged in user, the server will respond with a :term:`400 Bad Request` response.


Return Values
^^^^^^^^^^^^^

* :term:`200 OK`
* :term:`400 Bad Request`
* `403` (Unknown Token)
* `403` (Expired Token)
* `403` (Wrong user)
* `403` (Not allowed)
* `403` (Wrong password)
* :term:`500 Internal Server Error` (server fault, can not recover internally)
