Volto Blocks support
====================

.. note::
  plone.restapi package gives support for Volto Blocks providing a Dexterity behavior ``plone.restapi.behaviors.IBlocks`` that it is used to enable Volto Blocks in any content type.
  Volto then renders the Blocks engine for all the content types that have this behavior enabled.

Retrieving blocks on a content object
-------------------------------------

The ``plone.restapi.behaviors.IBlocks`` has two fields where existing blocks and their data are stored in the object (`blocks`) and the one where the current layout is stored (`blocks_layout`).
As they are fields in a Deterity behavior, both fields will be returned in a simple GET as attributes::

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

blocks objects will contain the tile metadata and the information to required to render them.


Adding blocks to an object
--------------------------

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
