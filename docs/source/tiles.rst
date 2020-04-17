Tiles
=====

.. note::
  The tiles endpoint currently match only partially (the GET endpoints) the default Plone implementation.

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
