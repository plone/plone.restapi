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

  @implementer(IBlockFieldDeserializationTransformer)
  @adapter(IBlocks, IBrowserRequest)
  class ImageBlockDeserializeTransformer(object):
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

  <subscriber factory=".blocks.ImageBlockDeserializeTransformer"
    provides="plone.restapi.interfaces.IBlockFieldDeserializationTransformer"/>

This would replace the ``url`` value to use resolveuid instead of hardcoding
the image path.

The ``block_type`` attribute needs to match the ``@type`` field of the block
value. The ``order`` attribute is used in sorting the subscribers for the same
field. Lower number has higher precedence (is executed first).

On the serialization path, a block value can be tweaked with a similar
transformer, for example on an imaginary Database Listing block type::

  @implementer(IBlockFieldDeserializationTransformer)
  @adapter(IBlocks, IBrowserRequest)
  class DatabaseQueryDeserializeTransformer(object):
      order = 100
      block_type = 'database_listing'

      def __init__(self, context, request):
          self.context = context
          self.request = request

      def __call__(self, value):
          value["items"] = db.query(value)    # pseudocode
          return value

Then register as a subscription adapter::

  <subscriber factory=".blocks.DatabaseQueryDeserializeTransformer"
    provides="plone.restapi.interfaces.IBlockFieldDeserializationTransformer"/>

Generic block transformers and smart fields
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can create a block transformer that applies to all blocks, by using `None`
as the value for `block_type`. The `order` field still applies, though. Using
the generic block transfomers enables us to create **smart block fields**,
which are handled differently. For example, any internal link stored as `url`
or `href` in a block value is converted (and stored) as a resolveuid-based URL,
then resolved back to a full URL on block serialization.

Another **smart field** is the `searchableText` field in a block value. It
needs to be a plain text value and it will be used in the `SearchableText`
value for the context item.

SearchableText indexing for blocks
----------------------------------

As the main consumer of plone.restapi's blocks, this functionality is specific to Volto blocks. By default searchable text (for Plone's SearchableText index) is extracted from `text` blocks.

To extract searchable text for other types of blocks, you need to write an adapter that can process that type of block.::

  @implementer(IBlockSearchableText)
  @adapter(IBlocks, IBrowserRequest)
  class ImageSearchableText(object):
      def __init__(self, context, request):
          self.context = context
          self.request = request

      def __call__(self, block_value):
          return block_value['alt_text']

See ``plone.restapi.interfaces.IBlockSearchableText`` for details. The ``__call__`` methods needs to return a string, for the text to be indexed.

This adapter needs to be registered as a named adapter, where the name is the same as the block type (its `@type` property from the block value).::

    <adapter name="image" factory=".indexers.ImageBlockSearchableText" />

