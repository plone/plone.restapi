.. _sharing:

Sharing
=======

Plone comes with a sophisticated user management system that allows to assign users and groups with global roles and permissions. Sometimes this in not enough though and you might want to give users the permission to access or edit a specific part of your website or a specific content object. This is where local roles (located in the Plone sharing tab) come in handy.


Retrieving Local Roles
----------------------

In plone.restapi, the representation of any content object will include a hypermedia link to the local role / sharing information in the ``sharing`` attribute:

.. code-block:: http

  GET /plone/folder HTTP/1.1
  Accept: application/json

.. code::

  HTTP 200 OK
  content-type: application/json

  {
    "@id": "http://localhost:55001/plone/folder",
    "@type": "Folder",
    ...
    "sharing": {
      "@id": "http://localhost:55001/plone/folder/@sharing",
      "title": "Sharing",
    }
  }

The sharing information of a content object can also be directly accessed by appending ``/@sharing`` to the GET request to the URL of a content object. E.g. to access the sharing information for a top-level folder, do:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/sharing_folder_get.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/sharing_folder_get.resp
   :language: http

The ``available_roles`` property contains the list of roles that can be
managed via the sharing page. It contains dictionaries with the role ID and
its translated ``title`` (as it appears on the sharing page).


Searching for principals
------------------------

Users and/or groups without a sharing entry can be found by appending the argument ``search`` to the query string. ie ``?search=admin``.
Global roles are marked with the string ``"global"``. Inherited roles are marked with the string ``"acquired"``.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/sharing_search.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/sharing_search.resp
   :language: http


Updating Local Roles
--------------------

You can update the 'sharing' information by sending a POST request to the object URL and appending ``/@sharing``, e.g. ``/plone/folder/@sharing``. E.g. say you want to give the ``AuthenticatedUsers`` group the ``Reader`` local role for a folder:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/sharing_folder_post.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/sharing_folder_post.resp
   :language: http
