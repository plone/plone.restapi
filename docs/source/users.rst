Users
=====

Available users in a Plone site can be created, queried, updated and deleted by interacting with the ``/@users`` endpoint on portal root (requires an authenticated user):

List Users
----------

To retrieve a list of all current users in the portal, call the ``/@users`` endpoint with a GET request:

.. example-code::

  .. code-block:: http-request

    GET /@users HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@users

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@users Accept:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@users', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

The server will respond with a list of all users in the portal:

.. literalinclude:: _json/users.json
   :language: js

The endpoint supports some basic filtering:

.. example-code::

  .. code-block:: http-request

    GET /@users?username=noam HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@users?username=noam

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@users username=='noam' Accept:application/json

  .. code-block:: python-requests

    requests.get('http://localhost:8080/Plone/@users', auth=('admin', 'admin'), headers={'Accept': 'application/json'}, params={'username': 'noam'})

The server will respond with a list the filtered users in the portal with username starts with the query.

The endpoint also takes a ``limit`` parameter that defaults to a maximum of 25 users at a time for performance reasons.

.. literalinclude:: _json/users_filtered_by_username.json
   :language: js


Create User
===========

You can create a user if you have the ``cmf.AddPortalMember`` permission. This is possible for anonymous users if self registration is enabled. The valid fields depend on the settings of the plone portal and should be in sync with the fields available/required in the plone registration forms (see below).

To create a new user, send a POST request to the global ``/@users`` endpoint with a JSON representation of the user you want to create in the body:

.. example-code::

  .. code-block:: http-request

    POST /@users HTTP/1.1
    Host: localhost:8080
    Accept: application/json
    Content-Type: application/json

    {
        'username': 'noam',
        'email': 'noam.chomsky@mit.edu',
        'password': 'colorlessgreenideas',
        'fullname': 'Noam Avram Chomsky',
        'home_page': 'web.mit.edu/chomsky',
        'description': 'Professor of Linguistics',
        'location': 'Cambridge, MA'
    }

  .. code-block:: curl

    curl -i -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"username": "noam", "email": "chomsky@mit.edu", "password": "colorlessgreenideas"}' --user admin:admin -X POST http://localhost:8080/Plone/@users

  .. code-block:: httpie

    http -a admin:admin POST http://localhost:8080/Plone/@users \\username=noam email=chomsky@mit.edu password=colorlessgreenideas Accept:application/json Content-Type:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@users', auth=('admin', 'admin'), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'username': 'noam', 'email': 'chomsky@mit.edu', 'password': 'colorlessgreenideas'})


Available and Required Fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The available and required fields depend on
* the settings ``Let users select their own passwords`` and ``Use email address as login name`` in the Plone Security control panel.
* For managers if they set a password for the new user or send out a reset password email.


  username (string)
  
    Required and allowed unless email as login name is enabled. 
    It needs to be a valid username and no duplicate username.

  password (string)

    ``Anonymous``: Required and allowed if ``Let users select their own passwords`` is enabled. If not allowed, a password reset mail is automatically send.

    ``Manager``: Either set password or user ``sendPasswordReset``

  email (string, valid email address)

     required. If email login is enabled it can't be a duplicate.

  sendPasswordReset (boolean)

     ``Anonymous``: not allowed

     ``Manager``: Either set ``sendPasswordReset`` or set a password

  roles (array)

     allowed for users with ``plone.app.controlpanel.UsersAndGroups``
     permission

  other properties

     Other Properties are allowed for users with
     ``plone.app.controlpanel.UsersAndGroups`` and will be set for the user
     if they are configured as MemberProperties. These properties won't
     raise an error if the usage or the properties are not allowed.


Response
~~~~~~~~

  201 (Created)

    If the user has been created successfully, the server will respond with a status 201 (Created). The 'Location' header contains the URL of the newly created user and the resource representation in the payload:

    .. literalinclude:: _json/users_created.json
       :language: js

  400 (Invalid data)

    FIXME: Define error response for invalid fields.


Read User
---------

To retrieve all details for a particular user, send a GET request to the ``/@users`` endpoint and append the user id to the URL:

.. example-code::

  .. code-block:: http-request

    GET /@users/noam HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@users/noam

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@users/noam Accept:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@users/noam', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

The server will respond with a 200 OK status code and the JSON representation of the user in the body:

.. literalinclude:: _json/users_noam.json
   :language: js


Update User
-----------

To update the settings of a user, send a PATCH request with the user details you want to amend to the URL of that particular user, e.g. if you want to update the email address of the admin user to:

.. example-code::

  .. code-block:: curl

    curl -i -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"email": "noam@mit.edu"}' --user admin:admin -X PATCH http://localhost:8080/Plone/@users

  .. code-block:: httpie

    http -a admin:admin PATCH http://localhost:8080/Plone/@users \\email=avram@mit.edu Accept:application/json Content-Type:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@users', auth=('admin', 'admin'), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'email': 'chomsky@mit.edu'})


A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/users_update.json
   :language: js


Delete User
-----------

To delete a user send a DELETE request to the ``/@users`` endpoint and append the user id of the user you want to delete, e.g. to delete the user with the id johndoe:

.. example-code::

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X DELETE http://localhost:8080/Plone/@users/noam

  .. code-block:: httpie

    http -a admin:admin DELETE http://localhost:8080/Plone/@users/noam Accept:application/json

  .. code-block:: python-requests

    requests.delete('http://localhost:8080/Plone/@users/noam', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/users_delete.json
   :language: js
