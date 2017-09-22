Control Panels
==============

Control panels in Plone allow you to configure the global site setup of a
Plone site. The @controlpanels endpoint in plone.restapi allows you to list
all existing control panels in a Plone site and to retrieve or edit the
settings of a specific control panel.

Most of the settings in the Plone control panels are based on plone.registry (since Plone 5.x). Therefore you can also use the @registry endpoint to
retrieve or manipulate site settings. The @controlpanels endpoint just gives
developers are more a convenience way of accessing the settings and makes it
easier to render control panels on the front-end.


.. note:: This is currently only implemented for Plone 5.


Listing Control Panels
----------------------

A list of all existing control panels in the portal can be retrieved by
sending a GET request to the @controlpanels endpoint:

..  http:example:: curl httpie python-requests
    :request: _json/controlpanels_get.req

Response:

.. literalinclude:: _json/controlpanels_get.resp
   :language: http

The following fields are returned:

- @id: hypermedia link to the control panel
- title: the title of the control panel
- group: the group where the control panel should show up (e.g. General, Content, Users, Security, Advanced, Add-on Configuration)


Retrieve a single Control Panel
-------------------------------

To retrieve a single control panel, send a GET request to the URL of the
control panel:

..  http:example:: curl httpie python-requests
    :request: _json/controlpanels_get_item.req

Response:

.. literalinclude:: _json/controlpanels_get_item.resp
   :language: http


The following fields are returned:

- @id: hypermedia link to the control panel
- title: title of the control panel
- group: group name of the control panel
- schema: JSON Schema of the control panel
- data: current values of the control panel


Updating a Control Panel with PATCH
-----------------------------------

To update the settings on a control panel send a PATCH request to control panel
resource:

..  http:example:: curl httpie python-requests
    :request: _json/controlpanels_patch.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

  HTTP/1.1 204 No Content

.. literalinclude:: _json/controlpanels_patch.resp
   :language: http
