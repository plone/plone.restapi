Groups
======

Available groups in a Plone site can be created, queried, updated and deleted by interacting with the ``/@groups`` endpoint on portal root (requires an authenticated user):

List Groups
-----------

To retrieve a list of all current groups in the portal, call the ``/@groups`` endpoint with a ``GET`` request:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/groups.req

The server will respond with a list of all groups in the portal:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/groups.resp
   :language: http

The endpoint supports some basic filtering:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/groups_filtered_by_groupname.req

The server will respond with a list the filtered groups in the portal with groupname starts with the query.

The endpoint also takes a ``limit`` parameter that defaults to a maximum of 25 groups at a time for performance reasons.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/groups_filtered_by_groupname.resp
   :language: http


Create Group
------------

To create a new group, send a ``POST`` request to the global ``/@groups`` endpoint with a JSON representation of the group you want to create in the body:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/groups_created.req

.. note::
    By default, "groupname" is a required field.

If the group has been created successfully, the server will respond with a status ``201 (Created)``. The ``Location`` header contains the URL of the newly created group and the resource representation in the payload:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/groups_created.resp
   :language: http


Read Group
----------

To retrieve all details for a particular group, send a ``GET`` request to the ``/@groups`` endpoint and append the group id to the URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/groups_get.req

The server will respond with a ``200 OK`` status code and the JSON representation of the group in the body:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/groups_get.resp
   :language: http

Batching is supported for the 'users' object.

Update Group
------------

To update the settings of a group, send a ``PATCH`` request with the group details you want to amend to the URL of that particular group:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/groups_update.req

.. note::
        The 'users' object is a mapping of a user_id and a boolean indicating adding or removing from the group.

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/groups_update.resp
   :language: http


Delete Group
------------

To delete a group send a ``DELETE`` request to the ``/@groups`` endpoint and append the group id of the group you want to delete:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/groups_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/groups_delete.resp
   :language: js
