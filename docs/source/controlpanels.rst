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


Listing Control Panels
----------------------

A list of all existing control panels in the portal can be retrieved by
sending a GET request to the @controlpanels endpoint::

    GET /plone/@controlpanels HTTP/1.1
    Accept: application/json
    Authorization: Basic YWRtaW46c2VjcmV0

Response::

    HTTP/1.1 200 OK
    Content-Type: application/json

    [
      {
        "@id": "http://localhost:55001/plone/@controlpanels/editing-controlpanel",
        "title": "Editing",
        "group": "Content",
      },
      {
        "@id": "http://localhost:55001/plone/@controlpanels/rules-controlpanel",
        "title": "Content Rules",
        "group": "Content",
      },
      ...
    ]

This following fields are returned:

- @id: hypermedia link to the control panel
- title: the title of the control panel
- group: the group where the control panel should show up (e.g. General, Content, Users, Security, Advanced, Add-on Configuration)


Retrieve a single Control Panel (WITHOUT EXPANSION)
---------------------------------------------------

To retrieve a single control panel, send a GET request to the URL of the
control panel::

    GET /plone/@controlpanels/editing-controlpanel HTTP/1.1
    Accept: application/json
    Authorization: Basic YWRtaW46c2VjcmV0

Response::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/@controlpanels/editing-controlpanel",
      "title": "Editing",
      "schema": {
        <JSON_SCHEMA>
      },
      "available_editors": ["TinyMCE", "None"],
      "default_editor": "TinyMCE",
      "ext_editor": False,
      "enable_link_integrity_checks": True,
      "lock_on_ttw_edit": True,
      "subjects_of_navigation_root": False,
    }


Retrieve a single Control Panel (ALTERNATIVE: WITH EXPANSION)
-------------------------------------------------------------

To retrieve a single control panel, send a GET request to the URL of the
control panel::

    GET /plone/@controlpanels/editing-controlpanel HTTP/1.1
    Accept: application/json
    Authorization: Basic YWRtaW46c2VjcmV0

Response (unexpanded)::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/@controlpanels/editing-controlpanel",
      "title": "Editing",
      "@components": {
        "schema": "http://localhost:55001/plone/@controlpanels/editing-controlpanel/@schema"
      },
      "available_editors": ["TinyMCE", "None"],
      "default_editor": "TinyMCE",
      "ext_editor": False,
      "enable_link_integrity_checks": True,
      "lock_on_ttw_edit": True,
      "subjects_of_navigation_root": False,
    }

Retrieve a control panel with expanded JSON schema::

    GET /plone/@controlpanels/editing-controlpanel?expansion=schema HTTP/1.1
    Accept: application/json
    Authorization: Basic YWRtaW46c2VjcmV0

Response (schema expanded)::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/@controlpanels/editing-controlpanel",
      "title": "Editing",
      "@components": {
        "schema": {
          <EMBEDDED_JSON_SCHEMA>
        }
      },
      "available_editors": ["TinyMCE", "None"],
      "default_editor": "TinyMCE",
      "ext_editor": False,
      "enable_link_integrity_checks": True,
      "lock_on_ttw_edit": True,
      "subjects_of_navigation_root": False,
    }

RFC: We can just always embed the JSON schema by default, or re-use the
expansion mechanism.

- PRO expansion: re-use existing pattern, can be used the same way for content
- CON expansion: more complex than just embedding the schema
- CON expansion: "@controlpanels/editing-controlpanel/@schema" might be hard to implement
- PRO simple: simple
- CON simple: introducing a new pattern


Updating a Control Panel with PATCH
-----------------------------------

To update the settings on a control panel send a PATCH request to control panel
resource::

    PATCH /plone/@controlpanels/editing-controlpanel HTTP/1.1
    Accept: application/json
    Authorization: Basic YWRtaW46c2VjcmV0

    {
      "default_editor": "CKeditor",
      "ext_editor": True,
    }

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response::

  HTTP/1.1 204 No Content
