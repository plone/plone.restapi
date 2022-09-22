---
myst:
  html_meta:
    "description": "The plone.restapi package gives support for Volto blocks providing a Dexterity behavior plone.restapi.behaviors.IBlocks."
    "property=og:description": "The plone.restapi package gives support for Volto blocks providing a Dexterity behavior plone.restapi.behaviors.IBlocks."
    "property=og:title": "Volto Blocks support"
    "keywords": "Plone, plone.restapi, REST, API, Volto, Blocks, support"
---

# Volto Blocks support

The `plone.restapi` package gives support for Volto blocks providing a Dexterity behavior `plone.restapi.behaviors.IBlocks`.
It is used to enable Volto blocks in any content type.
Volto then renders the blocks engine for all the content types that have this behavior enabled.


## Retrieving blocks on a content object

The `plone.restapi.behaviors.IBlocks` has two fields where existing blocks and their data are stored in the object (`blocks`).
The one where the current layout is stored (`blocks_layout`).
As they are fields in a Dexterity behavior, both fields will be returned in a `GET` request as attributes:

```http
GET /plone/my-document HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0
```

The server responds with a `Status 200`, and lists all stored blocks on that content object:

```http
GET /plone/my-document HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0
Content-Type: application/json

{
  "@id": "http://localhost:55001/plone/my-document",

  "...more response data...": "",

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
```

`blocks` objects will contain the title metadata and the information required to render them.


## Adding blocks to an object

Storing blocks is done via a default `PATCH` content operation:

```http
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
```


## Block serializers and deserializers

Practical experience has shown that it is useful to transform, server-side, the value of block fields on inbound (deserialization) and also outbound (serialization) operations.
For example, HTML field values are cleaned up using `portal_transforms`.
Or paths in image blocks are transformed to use `resolveuid`.

It is possible to influence the transformation of block values per block type.
For example, to tweak the value stored in an image type block, we can create a new subscriber as follows:

```python
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
```

Then register it as a subscription adapter:

```xml
<subscriber factory=".blocks.ImageBlockDeserializeTransformer"
  provides="plone.restapi.interfaces.IBlockFieldDeserializationTransformer"/>
```

This would replace the `url` value to use `resolveuid` instead of hard coding the image path.

The `block_type` attribute needs to match the `@type` field of the block value.
The `order` attribute is used in sorting the subscribers for the same field.
A lower number has higher precedence, that is, it is executed first.

On the serialization path, a block value can be tweaked with a similar transformer
For example, on an imaginary database listing block type:

```python
@implementer(IBlockFieldDeserializationTransformer)
@adapter(IBlocks, IBrowserRequest)
class DatabaseQueryDeserializeTransformer(object):
    order = 100
    block_type = 'database_listing'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, value):
        value["items"] = db.query(value)  # pseudocode
        return value
```

Then register it as a subscription adapter:

```xml
<subscriber factory=".blocks.DatabaseQueryDeserializeTransformer"
  provides="plone.restapi.interfaces.IBlockFieldDeserializationTransformer"/>
```


### Generic block transformers and smart fields

You can create a block transformer that applies to all blocks by using `None` as the value for `block_type`.
The `order` field still applies, though.
The generic block transformers enable us to create **smart block fields**, which are handled differently.
For example, any internal link stored as `url` or `href` in a block value is converted (and stored) as a `resolveuid`-based URL, then resolved back to a full URL on block serialization.

Another **smart field** is the `searchableText` field in a block value.
It needs to be a plain text value, and it will be used in the `SearchableText` value for the context item.

If you need to store "subblocks" in a block value, you should use the `blocks` smart field (or `data.blocks`).
Doing so integrates those blocks with the transformers.


## `SearchableText` indexing for blocks

As the main consumer of `plone.restapi`'s blocks, this functionality is specific to Volto blocks.
By default, searchable text (for Plone's `SearchableText` index) is extracted from `text` blocks.

To extract searchable text for other types of blocks, there are two approaches.


### Client side solution

The block provides the data to be indexed in its `searchableText` attribute:

```json
{
  "@type": "image",
  "align": "center",
  "alt": "Plone Conference 2021 logo",
  "searchableText": "Plone Conference 2021 logo",
  "size": "l",
  "url": "https://2021.ploneconf.org/images/logoandfamiliesalt.svg"
}
```

This is the preferred solution.


### Server side solution

For each new block, you need to write an adapter that will extract the searchable text from the block information:

```python
@implementer(IBlockSearchableText)
@adapter(IBlocks, IBrowserRequest)
class ImageSearchableText(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, block_value):
        return block_value['alt_text']
```

See `plone.restapi.interfaces.IBlockSearchableText` for details.
The `__call__` methods needs to return a string, for the text to be indexed.

This adapter needs to be registered as a named adapter, where the name is the same as the block type (its `@type` property from the block value):

```xml
<adapter name="image" factory=".indexers.ImageBlockSearchableText" />
```
