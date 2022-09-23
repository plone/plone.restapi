---
myst:
  html_meta:
    "description": "Relations between content items can be created, queried, and deleted using the /@relations and /@relations-catalog endpoints."
    "property=og:description": "Relations between content items can be created, queried, and deleted using the /@relations and /@relations-catalog endpoints."
    "property=og:title": "Relations"
    "keywords": "Plone, plone.restapi, REST, API, Relations, relations-catalog, endpoints"
---

(restapi-relations-label)=

# Relations

Plone's relations represent binary relationships between objects without using links or a hierarchy.

There are relations based on fields in a content type schema that are editable by users.
There are also relations without fields, such as `linkintegrity` or `working-copy`, that are created and deleted dynamically.
Every relation element has a source object, a target object, and the name of the relation.

Relations can be created, queried, and deleted by interacting through the `@relations` and `@relations-catalog` endpoints.

Reading relations with the `@relations` endpoint requires the `zope2.View` permission on the content object.
Creating and deleting relations requires the `cmf.ModifyContent` permission on the content object.

Interacting with the `@relations-catalog` endpoint requires the `cmf.ManagePortal` permission.


(restapi-listing-relations-of-an-object-label)=

## Listing relations of an object

By default, all relations are listed for a given source's context.

Alternatively you can list incoming relations by passing the parameter `backrelations=1`.

Optionally you can filter by relationship by passing the parameter `relation=<relationname>`.

Relation targets for which the user does not have the View permission are omitted from the results.

In all cases the results are grouped by relations, and the source and target are returned using the summarizer format.

Request outgoing relations for a content item `/plone/document`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get.req
```

Response with outgoing relations of `/plone/document`:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get.resp
:language: http
```

Request outgoing relations of a certain type for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.req
```

Response with outgoing relations for `/plone/document` of type `comprisesComponentPart`:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.resp
:language: http
```


Reading incoming relations for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_backrelations.req
```

Example response:

```{todo}
Add example response for this request.
```

Reading incoming relations of a certain type for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_backrelations_relationname.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_backrelations_relationname.resp
:language: http
```


(restapi-relations-creating-relations-for-an-object-label)=

## Creating relations for an object

You can create all kinds of relations between objects, then query for them later.
If the relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of that field is created or updated accordingly.

Adding a relation:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post.resp
:language: http
```

Adding multiple relations:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post_multiple.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post_multiple.resp
:language: http
```


(restapi-relations-deleting-relations-of-an-object-label)=

## Deleting relations of an object

In order to delete relation elements, you must provide either the source, target, or relation.
You can mix and match.

Delete all relations from this object to any target:

```
DELETE /plone/test-document/@relations
```

Delete all relations from any source to this object:

```
DELETE /plone/test-document/@relations?backrelations=1
```

Delete relations with name `comprisesComponentPart` from this object to any target:

```
DELETE /plone/test-document/@relations?relation=comprisesComponentPart
```

Delete relations with name `comprisesComponentPart` from any source to this object:

```
DELETE /plone/test-document/@relations?backrelations=1&relation=comprisesComponentPart
```

Delete relations with name `comprisesComponentPart` from any source to any target:

```
DELETE /plone/@relations-catalog?relation=comprisesComponentPart
```

If a deleted relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of the field is removed or updated accordingly.


(restapi-relations-the-relations-catalog-endpoint-label)=

## The `@relations-catalog` endpoint

The `@relations-catalog` endpoint allows to interact with all kinds of relations, individually or in bulk.
It is necessary to use a differently named endpoint for that purpose because the site root itself can be the source or target of relations.


(restapi-relations-getting-statistics-for-all-relations-label)=

### Getting statistics for all relations

```
GET /plone/@relations-catalog
```

This will return statistics on all existing relations.
That data will be used for the relations control panel.

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_catalog_get_stats.resp
:language: http
```


(restapi-relations-listing-relations-label)=

### Listing relations

To list relations, you must provide either the source, target, or relationship.
You can mix and match to inspect all kinds of relations.

List all relations of the type `comprisesComponentPart`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.resp
:language: http
```

List all relations outgoing from a certain object.

```
GET /plone/@relations-catalog?source=uuid1
```

This is equivalent to:

```
GET /plone/<item-with-uuid1>/@relations
```

List all relations outgoing from an object with the relation `comprisesComponentPart`:

```
GET /plone/@relations-catalog?source=uuid1&relation=comprisesComponentPart
```

This is equivalent to:

```
GET /plone/<item-with-uuid1>/@relations?relation=comprisesComponentPart
```

List all relations from any source to a certain object:

```
GET /plone/@relations-catalog?target=uuid1
```

This is equivalent to:

```
GET /plone/<item-with-uuid1>/@relations?backrelations=1
```

List all relations of type `comprisesComponentPart` from any source to a certain object:

```
GET /plone/@relations-catalog?target=uuid1&relation=comprisesComponentPart
```

This is equivalent to:

```
GET /plone/<item-with-uuid1>/@relations?backrelations=1&relation=comprisesComponentPart
```


(restapi-relations-creating-relations-label)=

### Creating relations

You can create all kinds of relations between objects and query for them later.

Adding a relation requires a source UUID, a target UUID, and the name of the relation.

If the relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of that field is created or updated accordingly.

Add relations:

```
POST /plone/@relations-catalog HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0
Content-Type: application/json

{
    "items": [
        {
            "source": "SomeUUID000000000000000000000001",
            "target": "SomeUUID000000000000000000000002",
            "relation": "comprisesComponentPart"
        },
        {
            "source": "AnotherUUID000000000000000000000001",
            "target": "AnotherUUID000000000000000000000002",
            "relation": "relatedItems"
        }
    ]
}
```

This is equivalent to the following request to the `@relations` endpoint:

```
POST /plone/@relations HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0
Content-Type: application/json

{
    "items": [
        {
            "source": "SomeUUID000000000000000000000001",
            "target": "SomeUUID000000000000000000000002",
            "relation": "comprisesComponentPart"
        },
        {
            "source": "AnotherUUID000000000000000000000001",
            "target": "AnotherUUID000000000000000000000002",
            "relation": "relatedItems"
        }
    ]
}
```


(restapi-relations-deleting-relations-label)=

### Deleting relations

If a deleted relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of the field is removed or updated accordingly.

Delete all relations of the type `comprisesComponentPart` from any source to any target:

```
DELETE /plone/@relations-catalog?relation=comprisesComponentPart
```

Delete all relations outgoing from a certain item:

```
DELETE /plone/@relations-catalog?source=uuid1
```

This is equivalent to:

```
DELETE /plone/<item-with-uuid1>/@relations
```

Delete all relations to a certain item:

```
DELETE /plone/@relations-catalog?target=uuid1
```

This is equivalent to:

```
DELETE /plone/<item-with-uuid1>/@relations?backrelations=1
```
