Groups
======

Available groups in a Plone site can be created, queried, updated and deleted by interacting with the ``/@groups`` endpoint on portal root (requires an authenticated user):

List Groups
-----------

To retrieve a list of all current groups in the portal, call the ``/@groups`` endpoint with a GET request:

.. example-code::

  .. code-block:: http-request

    GET /@groups HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@groups

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@groups Accept:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@groups', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

The server will respond with a list of all groups in the portal:

.. literalinclude:: _json/groups.json
   :language: js

The endpoint supports some basic filtering:

.. example-code::

  .. code-block:: http-request

    GET /@groups?groupname=ploneteam HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@groups?groupname=ploneteam

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@groups groupname=='ploneteam' Accept:application/json

  .. code-block:: python-requests

    requests.get('http://localhost:8080/Plone/@groups', auth=('admin', 'admin'), headers={'Accept': 'application/json'}, params={'groupname': 'noam'})

The server will respond with a list the filtered groups in the portal with groupname starts with the query.

The endpoint also takes a ``limit`` parameter that defaults to a maximum of 25 groups at a time for performance reasons.

.. literalinclude:: _json/groups_filtered_by_username.json
   :language: js


Create User
-----------

To create a new group, send a POST request to the global ``/@groups`` endpoint with a JSON representation of the group you want to create in the body:

.. example-code::

  .. code-block:: http-request

    POST /@groups HTTP/1.1
    Host: localhost:8080
    Accept: application/json
    Content-Type: application/json

    {
        'groupname': 'ploneteam',
        'title': 'Plone Team',
        'description': 'We are Plone',
        'email': 'ploneteam@plone.org',
    }

  .. code-block:: curl

    curl -i -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"username": "noam", "email": "chomsky@mit.edu", "password": "colorlessgreenideas"}' --user admin:admin -X POST http://localhost:8080/Plone/@groups

  .. code-block:: httpie

    http -a admin:admin POST http://localhost:8080/Plone/@groups \\username=noam email=chomsky@mit.edu password=colorlessgreenideas Accept:application/json Content-Type:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@groups', auth=('admin', 'admin'), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'username': 'noam', 'email': 'chomsky@mit.edu', 'password': 'colorlessgreenideas'})

.. note::
    By default, "username", and "password" are required fields. If email login is enabled, "email" and "password" are required fields. All other fields in the example are optional.

If the user has been created successfully, the server will respond with a status 201 (Created). The 'Location' header contains the URL of the newly created user and the resource representation in the payload:

.. literalinclude:: _json/groups_created.json
   :language: js


Read Group
----------

To retrieve all details for a particular user, send a GET request to the ``/@groups`` endpoint and append the user id to the URL:

.. example-code::

  .. code-block:: http-request

    GET /@groups/ploneteam HTTP/1.1
    Host: localhost:8080
    Accept: application/json

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X GET http://localhost:8080/Plone/@groups/ploneteam

  .. code-block:: httpie

    http -a admin:admin GET http://localhost:8080/Plone/@groups/ploneteam Accept:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@groups/ploneteam', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

The server will respond with a 200 OK status code and the JSON representation of the user in the body:

.. literalinclude:: _json/groups_ploneteam.json
   :language: js


Update User
-----------

To update the settings of a user, send a PATCH request with the user details you want to amend to the URL of that particular user, e.g. if you want to update the email address of the admin user to:

.. example-code::

  .. code-block:: curl

    curl -i -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"email": "noam@mit.edu"}' --user admin:admin -X PATCH http://localhost:8080/Plone/@groups

  .. code-block:: httpie

    http -a admin:admin PATCH http://localhost:8080/Plone/@groups \\email=avram@mit.edu Accept:application/json Content-Type:application/json

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@groups', auth=('admin', 'admin'), headers={'Accept': 'application/json', 'Content-Type': 'application/json'}, params={'email': 'chomsky@mit.edu'})


A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/groups_update.json
   :language: js


Delete Group
------------

To delete a group send a DELETE request to the ``/@groups`` endpoint and append the user id of the user you want to delete, e.g. to delete the user with the id johndoe:

.. example-code::

  .. code-block:: curl

    curl -i -H "Accept: application/json" --user admin:admin -X DELETE http://localhost:8080/Plone/@groups/ploneteam

  .. code-block:: httpie

    http -a admin:admin DELETE http://localhost:8080/Plone/@groups/ploneteam Accept:application/json

  .. code-block:: python-requests

    requests.delete('http://localhost:8080/Plone/@groups/ploneteam', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/groups_delete.json
   :language: js
