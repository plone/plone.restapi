Blocks
=====

.. note::
  The blocks endpoint currently match only partially (the GET endpoints) the default Plone implementation.
  The serialization of blocks didn't match the Mosaic (and plone.app.blocks) implementation and it's done to
  not rely on those technologies. The serialization of the block information on objects are subject to change in
  the future to extend or improve features.

A block in Plone is an HTML snippet that can contain arbitrary content (e.g. text, images, videos).


Listing available blocks
-----------------------

.. note::
  This endpoint currently does not return any data. The functionality needs to be implemented.

List all available blocks type by sending a GET request to the @blocks endpoint on the portal root::

  GET /plone/@blocks HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a `Status 200` and list all available blocks::

  HTTP/1.1 200 OK
  Content-Type: application/json
  [
    {
      "@id": "http://localhost:55001/plone/@blocks/title",
      "title": "Title block",
      "description": "A field block that will show the title of the content object",
    },
    {
      "@id": "http://localhost:55001/plone/@blocks/description",
      "title": "Description block",
      "description": "A field block that will show the description of the content object",
    },
  ]


Retrieve JSON schema of an individual block
------------------------------------------

.. note::
  This endpoint currently does not return any data. The functionality needs to be implemented.

Retrieve the JSON schema of a specific block by calling the '@blocks' endpoint with the id of the block::

  GET /plone/@blocks/title HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a JSON schema definition for that particular block::

  HTTP/1.1 200 OK
  Content-Type: application/json+schema

  {
    "properties": {
      "title": {
        "description": "",
        "title": "Title",
        "type": "string"
      },
      ...
    },
    "required": [
      "title",
    ],
    "title": "Title Tile",
    "type": "object"
  }


Retrieving blocks on a content object
------------------------------------

Blocks data are stored in the objects via a Dexterity behavior `plone.blocks`. It has two attributes that stores existing blocks in the object (`blocks`) and the current layout (`blocks_layout`).
As it's a dexterity behavior, both attributes will be returned in a simple GET::

  GET /plone/my-document HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a `Status 200` and list all stored blocks on that content object::

  GET /plone/my-document HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/my-document",
    ...
    "blocks_layout": [
      "#title-1",
      "#description-1",
      "#image-1"
    ],
    "blocks": {
      "#title-1": {
        "@type": "title"
      },
      "#description-1": {
        "@type": "Description"
      },
      "#image-1": {
        "@type": "Image",
        "image": "<some random url>"
      }
    }
  }

Blocks objects will contain the block metadata and the information to render it.


Adding blocks to an object
-------------------------

Storing blocks is done also via a default PATCH content operation::

  PATCH /plone/my-document HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Content-Type: application/json

  {
    "blocks_layout": [
      "#title-1",
      "#description-1",
      "#image-1"
    ],
    "blocks": {
      "#title-1": {
        "@type": "title"
      },
      "#description-1": {
        "@type": "Description"
      },
      "#image-1": {
        "@type": "Image",
        "image": "<some random url>"
      }
    }
  }

If the block has been added, the server responds with a `204` status code.


Proposal on saving blocks layout
--------------------------------

.. note::
  This is not implemented (yet) in the blocks_layout field, but it's a proposal on
  how could look like in the future. For now, we stick with the implementation shown in
  previous sections.

They might be serialized using this structure::

  [
    [
      id: UUID,
      columns: [
        {
          id: UUID, // column UUID
          size: int // the size of the column
          rows: [
            {
              id: UUID, // inner row UUID
              cells: [
                {
                  id: UUID, // cell UUID
                  component: string
                  content: {
                    // block fields serialization (or block id referal)
                  },
                  size: int
                },
              ]
            }
          ]
        },
      ]
    ], // row 1
    [], // row 2
  ]

It tries to match the usual way of CSS frameworks to map grid systems. So we have:

row (orderables up/down) -> column (resizables on width) -> row -> cell (actual block content)

Rows are orderable vertically, columns resizables horizontally and cells can be
moved around to an specific inner row.
