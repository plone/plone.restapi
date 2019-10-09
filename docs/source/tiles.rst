Tiles
=====

.. note::
  The tiles endpoint currently match only partially (the GET endpoints) the default Plone implementation.
  The serialization of tiles didn't match the Mosaic (and plone.app.blocks) implementation and it's done to
  not rely on those technologies. The serialization of the tile information on objects are subject to change in
  the future to extend or improve features.

A tile in Plone is an HTML snippet that can contain arbitrary content (e.g. text, images, videos).


Listing available tiles
-----------------------

.. note::
  This endpoint currently does not return any data. The functionality needs to be implemented.

List all available tiles type by sending a GET request to the @tiles endpoint on the portal root::

  GET /plone/@tiles HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a `Status 200` and list all available tiles::

  HTTP/1.1 200 OK
  Content-Type: application/json
  [
    {
      "@id": "http://localhost:55001/plone/@tiles/title",
      "title": "Title tile",
      "description": "A field tile that will show the title of the content object",
    },
    {
      "@id": "http://localhost:55001/plone/@tiles/description",
      "title": "Description tile",
      "description": "A field tile that will show the description of the content object",
    },
  ]


Retrieve JSON schema of an individual tile
------------------------------------------

.. note::
  This endpoint currently does not return any data. The functionality needs to be implemented.

Retrieve the JSON schema of a specific tile by calling the '@tiles' endpoint with the id of the tile::

  GET /plone/@tiles/title HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a JSON schema definition for that particular tile::

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


Retrieving tiles on a content object
------------------------------------

Tiles data are stored in the objects via a Dexterity behavior `plone.tiles`. It has two attributes that stores existing tiles in the object (`tiles`) and the current layout (`tiles_layout`).
As it's a dexterity behavior, both attributes will be returned in a simple GET::

  GET /plone/my-document HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a `Status 200` and list all stored tiles on that content object::

  GET /plone/my-document HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/my-document",
    ...
    "tiles_layout": [
      "#title-1",
      "#description-1",
      "#image-1"
    ],
    "tiles": {
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

Tiles objects will contain the tile metadata and the information to render it.


Adding tiles to an object
-------------------------

Storing tiles is done also via a default PATCH content operation::

  PATCH /plone/my-document HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Content-Type: application/json

  {
    "tiles_layout": [
      "#title-1",
      "#description-1",
      "#image-1"
    ],
    "tiles": {
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

If the tile has been added, the server responds with a `204` status code.


Proposal on saving tiles layout
--------------------------------

.. note::
  This is not implemented (yet) in the tiles_layout field, but it's a proposal on
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
                    // tile fields serialization (or tile id referal)
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

row (orderables up/down) -> column (resizables on width) -> row -> cell (actual tile content)

Rows are orderable vertically, columns resizables horizontally and cells can be
moved around to an specific inner row.
