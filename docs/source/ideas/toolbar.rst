Toolbar Draft
-------------

@toolbar endpoint which is context sensible and expandable.


Request::

  GET localhost:8080/Plone/folder/@toolbar
  Accept application/json

Reponse if user does not have the ShowToolbar permission::

  401 Unauthorized

Permissions only response::

  {
    '@id': 'localhost:8080/Plone/@toolbar',
    items: [
      'contents': true,
      'edit': true,
      'view': true,
      'translate': true,
      'add-new': true,
      'state': true,
      'actions': true,
      'display': true,
      'manage-portlets': true,
      'history': true,
      'sharing': true,
      'user': true,
    ]
  }

Questions:

- Just a list? items = ['contents', 'edit', ...]
- Nested? 'actions': {'copy': true, 'cut': true, 'paste': true}
- Wouldn't is be enough if the client would just ask for specific permissions?
- Alternative: a permissions endpoint that can be queried as expandable?

Response (for admin)::

  {
    '@id': 'localhost:8080/Plone/@toolbar',
    'items': [
      # CONTENTS: LINK ON REACT LEVEL
      # JUST RETURN true IF USER HAS 'LIST FOLDER CONTENTS' PERMISSION?
      'contents': true
      # EDIT: LINK ON REACT LEVEL
      # JUST RETURN true IF USER HAS 'MODIFY PORTAL CONTENT' PERMISSION?
      'edit': true
      # VIEW: LINK ON REACT LEVEL
      # JUST RETURN true IF USER HAS 'VIEW' PERMISSION?
      'view': true,
      'translate': {
        # -> LATER
      },
      'add-new': {
        'Collection': true,
        'Event': true,
        ...
        # HOW DO WE HANDLE MODIFY RESTRICTIONS?
      },
      'state': {
        # WE ALREADY HAVE THAT INFORMATION IN THE @WORKFLOW view
      },
      'actions': {
        'cut': true,
        'copy': true,
        'delete': true,
        'rename': true,
        # DO WE WANT TO INCLUDE THE ACTION URLs ON THE BACKEND?
        'cut': {
          '@id': 'localhost:8080/Plone/folder/@cut',
          'title': 'Cut',
        },
        'copy': {
          '@id': 'localhost:8080/Plone/folder/@copy',
          'title': 'Copy',
        },
        'move': {
          '@id': 'localhost:8080/Plone/folder/@move',
          'title': 'Move',
        },

      },
      'display': {
        'folder_summary_view': true,
        'folder_full_view': true,
        'folder_tabular_view': true,
        'atct_album_view': true,
        'folder_listing': true,
        'Item: Welcome to Plone 5': true,
        # HOW DO WE HANDLE CONTENT AS DEFAULT?
        'Change content item as default view...'
        # HYPERMEDIA
        [
          {
            '@id': 'localhost:8080/Plone/folder/@display=folder_summary_view
            'title': 'Folder Summary View'
          }
          # A BACKEND CALL LIKE THIS DOES NOT EXIST YET, WE HAVE THE LAYOUT ATTR THOUGH
      },
      'manage-portlets': {
        'Plone Footerportlets': true,
        'Plone Lefcolumn': true,
        'Plone Rightcolumn': true,
        # DO WE JUST WANT TO LINK TO THE VIEWS OR EDIT THIS WITH PASTANAGA INLINE?
      },
      'history': {
        # INLINE IN PASTANAGA OR JUST LINK?
      },
      'sharing': {
        # INLINE IN PASTANAGA OR JUST LINK?
      },
      'user': {
        # INLINE IN PASTANAGA OR JUST LINK?
      },
    ]
  }
