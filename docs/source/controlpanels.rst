Control Panels
==============

Control panels in Plone allow you to configure the global site setup of a
Plone site. The ``@controlpanels`` endpoint in plone.restapi allows you to list
all existing control panels in a Plone site and to retrieve or edit the
settings of a specific control panel.

Most of the settings in the Plone control panels are based on plone.registry (since Plone 5.x). Therefore you can also use the ``@registry`` endpoint to
retrieve or manipulate site settings. The ``@controlpanels`` endpoint just gives
developers are more a convenience way of accessing the settings and makes it
easier to render control panels on the front-end.


.. note:: This is currently only implemented for Plone 5.


Listing Control Panels
----------------------

A list of all existing control panels in the portal can be retrieved by
sending a GET request to the ``@controlpanels`` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_get.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_get.resp
   :language: http

The following fields are returned:

- ``@id``: hypermedia link to the control panel
- ``title``: the title of the control panel
- ``group``: the group where the control panel should show up (e.g. General, Content, Users, Security, Advanced, Add-on Configuration)


Retrieve a single Control Panel
-------------------------------

To retrieve a single control panel, send a GET request to the URL of the
control panel:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_get_item.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_get_item.resp
   :language: http


The following fields are returned:

- ``@id``: hypermedia link to the control panel
- ``title``: title of the control panel
- ``group``: group name of the control panel
- ``schema``: JSON Schema of the control panel
- ``data``: current values of the control panel


Updating a Control Panel with PATCH
-----------------------------------

To update the settings on a control panel send a PATCH request to control panel
resource:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_patch.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

  HTTP/1.1 204 No Content

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_patch.resp
   :language: http


Control Panels not based on plone.registry
------------------------------------------

Control panel which are not based on plone.registry have a custom ``@controlpanels/:panel`` endpoint implementation.

.. _dexterity-types:

Dexterity Types
^^^^^^^^^^^^^^^

``@controlpanels/dexterity-types`` is a custom control panel endpoint, that will allow you to add, remove and configure available :ref:`types`

Reading or writing Dexterity Content Types require the ``plone.schemaeditor.ManageSchemata`` permission.

======= =============================================== ==============================================
Verb    URL                                             Action
======= =============================================== ==============================================
GET     ``/@controlpanels/dexterity-types``             List configurable content-types
POST    ``/@controlpanels/dexterity-types``             Creates a new content-type
GET     ``/@controlpanels/dexterity-types/{type-id}``   Get the current state of the content-type
PATCH   ``/@controlpanels/dexterity-types/{type-id}``   Update the content-type details
DELETE  ``/@controlpanels/dexterity-types/{type-id}``   Remove content-type
======= =============================================== ==============================================


Listing Dexterity Content Types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To list the available content-types send a GET request to ``@controlpanels/dexterity-types``

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity.resp
   :language: http

The following fields are returned:

- ``@id``: hypermedia link to the control panel
- ``title``: title of the control panel
- ``group``: group name of the control panel
- ``schema``: JSON Schema of the control panel
- ``data``: current values of the control panel
- ``items``: list of configurable content-types.


Creating a new Dexterity Type with POST
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To create a new content-type, send a POST request to the ``/@controlpanels/dexterity-types`` endpoint.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_post_dexterity_item.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_post_dexterity_item.resp
   :language: http


Reading a Dexterity Type with GET
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

After a successful POST, access the content-type by sending a GET request to the ``/@controlpanels/dexterity-types/{type-id}``:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity_item.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_get_dexterity_item.resp
   :language: http


Updating a Dexterity Type with PATCH
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To update an existing content-type we send a PATCH request to the server.
PATCH allows to provide just a subset of the resource (the values you actually want to change).

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_patch_dexterity_item.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_patch_dexterity_item.resp
   :language: http


Removing a Dexterity Type with DELETE
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete an existing content-type by sending a DELETE request to the URL of an existing content-type:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/controlpanels_delete_dexterity_item.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/controlpanels_delete_dexterity_item.resp
   :language: http
