---
myst:
  html_meta:
    "description": "Throughout the REST API, content needs to be serialized and deserialized to and from JSON representations."
    "property=og:description": "Throughout the REST API, content needs to be serialized and deserialized to and from JSON representations."
    "property=og:title": "Serialization"
    "keywords": "Plone, plone.restapi, REST, API, Serialization"
---

# Serialization

Throughout the REST API, content needs to be serialized and deserialized to and from JSON representations.

In general, the format used for serializing content when reading from the API is the same as is used to submit content to the API for writing.


## Basic Types

Basic Python data types that have a corresponding type in JSON, such as integers or strings, will be translated between the Python type and the respective JSON type.


## Dates and Times

Since JSON does not have native support for dates and times, the Python and Zope `datetime` types will be serialized to an ISO 8601 date string.

| Python                               | JSON                    |
| ------------------------------------ | ----------------------- |
| `time(19, 45, 55)`                   | `"19:45:55"`            |
| `date(2015, 11, 23)`                 | `"2015-11-23"`          |
| `datetime(2015, 11, 23, 19, 45, 55)` | `"2015-11-23T19:45:55"` |
| `DateTime("2015/11/23 19:45:55")`    | `"2015-11-23T19:45:55"` |


## RichText fields

RichText fields will be serialized as follows:

A `RichTextValue` such as the following:

```python
RichTextValue(u'<p>Hallöchen</p>',
              mimeType='text/html',
              outputMimeType='text/html')
```

…will be serialized to:

```json
{
  "data": "<p>Hall\u00f6chen</p>",
  "content-type": "text/html",
  "encoding": "utf-8"
}
```


## File / Image Fields


### Download (serialization)

For download, a file field will be serialized to a mapping that contains the file's most basic metadata, and a hyperlink that the client can follow to download the file:

```json
{
  "...": "",
  "@type": "File",
  "title": "My file",
  "file": {
    "content-type": "application/pdf",
    "download": "http://localhost:55001/plone/file/@@download/file",
    "filename": "file.pdf",
    "size": 74429
  }
}
```

That URL in the `download` property points to the regular Plone download view.
The client can send a `GET` request to that URL with an `Accept` header containing the MIME type indicated in the `content-type` property, and will get a response containing the file.

Image fields are serialized in the same way, except that their serialization contains their `width` and `height`, and an additional property `scales` that contains a mapping with the available image scales.
Image URLs are created using the UID-based URL that changes each time the image is modified, allowing these URLs to be properly cached:

```json
{
  "icon": {
    "download": "http://localhost:55001/plone/image/@@images/8eed3f80-5e1f-4115-85b8-650a10a6ca84.png",
    "height": 32,
    "width": 24
  },
  "large": {
    "download": "http://localhost:55001/plone/image/@@images/0d1824d1-2672-4b62-9277-aeb220d3bf15.png",
    "height": 768,
    "width": 576
  },
  "..." : {}
}
```

### Upload (deserialization)

For file or image fields, the client must provide the file's data as a mapping containing the file data and some additional metadata:

- `data` - the base64-encoded contents of the file
- `encoding` - the encoding you used to encode the data, usually `base64`
- `content-type` - the MIME type of the file
- `filename` - the name of the file, including its extension

```json
{
  "...": "",
  "@type": "File",
  "title": "My file",
  "file": {
    "data": "TG9yZW0gSXBzdW0uCg==",
    "encoding": "base64",
    "filename": "lorem.txt",
    "content-type": "text/plain"
  }
}
```


## Relations


### Serialization

A `RelationValue` will be serialized to a short summary representation of the referenced object:

```json
{
  "@id": "http://nohost/plone/doc1",
  "@type": "DXTestDocument",
  "title": "Document 1",
  "description": "Description"
}
```

The `RelationList` containing that reference will be represented as a list in JSON.


### Deserialization

In order to set a relation when creating or updating content, you can use one of several ways to specify relations:

- UID
- path
- URL
- intid


Specify relations by UID:

```json
{
  "relatedItems": [
    "158e5361282647e39bf0698fe238814b",
    "5597250bda4b41eab6ed37cd25fb0979"
  ]
}
```

Specify relations by path:

```json
{
  "relatedItems": ["/page1", "/page2"]
}
```

Specify relations by URL:

```json
{
  "relatedItems": [
    "http://localhost:8080/Plone/page1",
    "http://localhost:8080/Plone/page2"
  ]
}
```

Specify relations by intid:

```json
{
  "relatedItems": [347127075, 347127076]
}
```


## Next, Previous, and Parent Navigation

The response body of a `GET` request contains three attributes that allow navigating to the parent and to the next and previous sibling in the container in which the current document is located.


### Parent

The `parent` attribute points to the parent container of the current content object:

```json
{
  "parent": {
    "@id": "http://nohost/plone/folder-with-items",
    "@type": "Folder",
    "title": "Folder with items",
    "description": "This is a folder with two documents"
  }
}
```


### Previous Item

The `previous_item` attribute points to the sibling that is located before the current element in the parent container.
Plone uses the `getObjectPositionInParent` attribute to sort content objects within a folderish container:

```json
{
  "previous_item": {
    "@id": "http://nohost/plone/folder-with-items/item-1",
    "@type": "Document",
    "title": "Item 1",
    "description": "This the previous item"
  }
}
```

### Next Item

The `next_item` attribute points to the sibling that is located after the current element in the parent container.
Plone uses the `getObjectPositionInParent` attribute to sort content objects within a folderish container):

```json
{
  "next_item": {
    "@id": "http://nohost/plone/folder-with-items/item-2",
    "@type": "Document",
    "title": "Item 2",
    "description": "This the next item"
  }
}
```
