Tiles
=====

A tile is an HTML snippet that can contain arbitrary content (e.g. text, images, videos).

The @tiles endpoint is context specific.
Called on the portal root it will list all available tiles,
and allows to retrieve the JSON schema for those tiles.

If called on a content object, it will return the tiles that are actually stored on that content object.

Listing available tiles
-----------------------

List all available tiles type by sending a GET request to the @tiles endpoint on the portal roots::

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

Retrieve Tile JSON schema
-------------------------

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

Retrieve a list of tiles stored on a content object by calling the @tiles endpoint on a content object::

  GET /plone/my-document/@tiles HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

The server responds with a `Status 200` and list all stored tiles on that content object::

  HTTP/1.1 200 OK
  Content-Type: application/json
  {
    "@id": "http://localhost:55001/plone/my-document",
    ...
    "tiles": [
      {
        "@id": "http://localhost:55001/plone/my-document/@tiles/my-title",
        "type": "title",
      },
      {
        "@id": "http://localhost:55001/plone/my-document/@tiles/my-description",
        "type": "description",
      },
      {
        "@id": "http://localhost:55001/plone/my-document/@tiles/image-1",
        "type": "image",
        "data": {
          "image": "<some random url>",
          "caption": "My pony",
        },
      },
      {
        "type": "image",
        "data": {
          "image": "<some random url>",
          "caption": "My cow",
        },
      },
    ]
  }

The '@tiles' endpoint is an expandable endpoint that can be embedded in the response to a GET request on a content object::

  GET /plone/my-document?expand=tiles HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

  {
    "@id": "http://localhost:55001/plone/my-document",
    "@type": "Document",
    "@components": {
      "tiles": [
        {
          "@id": "http://localhost:55001/plone/my-document/@tiles/my-title",
          "type": "title",
        },
        {
          "@id": "http://localhost:55001/plone/my-document/@tiles/my-description",
          "type": "description",
        },
        {
          "@id": "http://localhost:55001/plone/my-document/@tiles/image-1",
          "type": "image",
          "data": {
            "image": "<some random url>",
            "caption": "My pony",
          },
        },
        {
          "type": "image",
          "data": {
            "image": "<some random url>",
            "caption": "My cow",
          },
        },
      ],
      ...
    }
  }

Adding tiles
------------

To add a tile to a content object do a POST request to the tile URL, e.g.
if you want to add a title tile::

  POST /plone/my-document/@tiles/title HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Content-Type: application/json

  {
      "@type": "Title",
      "title": "This is a title tile"
  }

If the tile has been added, the server responds with the `201 Created` status code.
The ‘Location’ header contains the URL of the newly created resource and the resource representation in the payload::

  HTTP/1.1 201 Created
  Content-Type: application/json
  Location: http://localhost:55001/plone/my-document/@tiles/title
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

Updating a tile with PATCH
--------------------------

To update an existing tile, we send a PATCH request to the URL of the tile::

  PATCH /plone/my-document/@tiles/title HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Content-Type: application/json
  {
      "title": "New tile titlee"
  }

PATCH allows to provide just a subset of the resource (the values you actually want to change).

A successful response to a PATCH request will be indicated by a `204 No Content` response by default::

  HTTP/1.1 204 No Content
  Successful Response (200 OK)

You can get the object representation by adding a Prefer header with a value of return=representation to the PATCH request.
In this case, the response will be a 200 OK::

  PATCH /plone/my-document/@tiles/title HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0
  Prefer: return=representation
  Content-Type: application/json

  {
      "title": "New tile title"
  }

Removing a tile with DELETE
---------------------------

We can delete an existing tile by sending a DELETE request::

  DELETE /plone/my-document/@tiles/title HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

A successful response will be indicated by a `204 No Content` response::

  HTTP/1.1 204 No Content