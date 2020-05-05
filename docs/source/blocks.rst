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

Block serializers and deserializers
-----------------------------------

Practical experience has shown that it is useful to transform, server-side, the
value of block fields on inbound (deserialization) and also outbound
(serialization) operations. For example, HTML field values are cleaned up using
``portal_transforms``, paths in Image blocks are transformed to use resolveuid
and so on.

It is possible to influence the transformation of block values per block type.
For example, to tweak the value stored in Image type block, we can create a
new subscriber like::

  @implementer(IBlockDeserializer)
  @adapter(IBlocks, IBrowserRequest)
  class ImageBlockDeserializer(object):
      order = 100
      block_type = 'image'

      def __init__(self, context, request):
          self.context = context
          self.request = request

      def __call__(self, value):
          portal = getMultiAdapter(
              (self.context, self.request), name="plone_portal_state"
          ).portal()
          url = value.get('url', '')
          deserialized_url = path2uid(
              context=self.context, portal=portal,
              href=url
          )
          value["url"] = deserialized_url
          return value

Then register as a subscription adapter::

  <subscriber factory=".blocks.ImageBlockDeserializer"
    provides="plone.restapi.interfaces.IBlockDeserializer"/>

This would replace the ``url`` value to use resolveuid instead of hardcoding
the image path.

The ``block_type`` attribute needs to match the ``@type`` field of the block
value. The ``order`` attribute is used in sorting the subscribers for the same
field. Lower number has higher precedence (is executed first).
