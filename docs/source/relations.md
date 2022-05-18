---
html_meta:
  "description": "Relations between content items can be created, queried and deleted using the /@relations endpoint."
  "property=og:description": "Relations between content items can be created, queried and deleted using the /@relations and /@relations-catalog endpoints."
  "property=og:title": "Relations"
  "keywords": "Plone, plone.restapi, REST, API, Relations"
---

# Relations

Relations model relationships between objects without using links or a hierarchy.
There are relations based on fields in a content-type schema that are editable by users.
There are also relations without fields (e.g. linkintegrity or working-copy) that are created and deleted dynamically.
Every relation has a source object, a target object and the name of the relation.

Relations can be created, queried and deleted by interacting through the `@relations` and `@relations-catalog` endpoints.

Reading relations with the `@relations` endpoint requires the `zope2.View` permission on the content object.
Creating and deleting relations requires the `cmf.ModifyContent` permission on the content object.

Iteracting with the `@relations-catalog` endpoint requires the `cmf.ManagePortal` permission.

## The `@relations` endpoint

### Listing relations for an object

By default all relations are listed for which the context is the source.
Alternatively you can list incoming relations by passing the parameter `backrelations=1`.
Optionally you can filter by relationship by passing the parameter `relation=<relationname>`.
Relation-targets for which the user does not have the View-permission are omitted from the results.
In all cases the results are grouped by relations and the source and target are returned using the summarizer format.

Reading outgoing relations for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_get.req
```

Example response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/relations_get.resp
:language: http
```

Reading outgoing relations of a certain type for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_relationname_get.req
```

Example response:

TODO

Reading incoming relations for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_backrelations_get.req
```

Example response:

TODO

Reading incoming relations of a certain type for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_backrelations_relationname_get.req
```

Example response:

TODO

## Creating relations for an object

You can create all kinds of relations between objects and query for them later.
If the relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of that field is created/updated accordingly.

Adding a relation:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_post.req
```

Example response:

TODO

Add multiple relations:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_multiple_post.req
```

Example response:

TODO


## Deleting relations

In order to delete relation(s), you must provide either source, target, or relationship.
You can mix and match.

Delete all relations from this object to any target

```
DELETE /plone/test-document/@relations
```

Delete all relations from any source to this object

```
DELETE /plone/test-document/@relations?backrelations=1
```

Delete relations with name "friend" from this object to any target

```
DELETE /plone/test-document/@relations?relation=friend
```

Delete relations with name "uncle" from any source to this object

```
DELETE /plone/test-document/@relations?backrelations=1&relation=uncle
```

Delete relations with name "enemy" from any source to any target

```
DELETE /plone/@relations-catalog?relation=enemy
```

If a deleted relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of the field is removed/updated accordingly.


## The `@relations-catalog` endpoint

The `@relations-catalog` endpoint allows to interact with all kinds of relations individually or in bulk.
It is necessary to use a differently named endpoint for that purpose because the site-root itself can be the source or target of relations.


### Getting statistics for all relations

```
GET /plone/@relations-catalog
```

This will return statistics on all existing relations.
That data will used for the relations-controlpanel.

```
{
    "@id": "http://localhost:55001/plone/@relations-catalog",
    "items": {
        "relatedItems": 66,
        "isReferencing": 233
    }
    "broken": {
        "relatedItems": 2,
        "isReferencing": 444
    }
}
```



### Listing relations

To list relation(s), you must provide either source, target or relationship.
You can mix and match to inspect all kind of relations.

List all relations of the type "friend":

```
GET /plone/@relations-catalog?relation=friend
```

List all relations outgoing from a certain object.

```
GET /plone/@relations-catalog?source=uuid1
```

This is equivalent to

```
GET /plone/<item-with-uuid1>/@relations
```


List all relations outgoing from an object with the relation `uncle`

```
GET /plone/@relations-catalog?source=uuid1&relation=uncle
```

This is equivalent to

```
GET /plone/<item-with-uuid1>/@relations?relation=uncle
```

List all relations from any source to a certain object

```
GET /plone/@relations-catalog?target=uuid1
```

This is equivalent to:

```
GET /plone/<item-with-uuid1>/@relations?backrelations=1
```

List all relations of type `uncle` from any source to a certain object

```
GET /plone/@relations-catalog?target=uuid1&relation=uncle
```

This is equivalent to:

```
GET /plone/<item-with-uuid1>/@relations?backrelations=1&relation=uncle
```

### Creating relations

You can create all kinds of relations between objects and query for them later.

Adding a relation required a source uuid, a target uuid and the name of the relation.

If the relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of that field is created/updated accordingly.

Add relation:

```
POST /plone/@relations
POST /plone/@relations HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0
Content-Type: application/json

{
    "items": [
        {
            "source": "SomeUUID000000000000000000000001",
            "target": "SomeUUID000000000000000000000002",
            "relation": "evil_mastermind"
        }
    ]
}
```

Add multiple relations:

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
            "relation": "evil_mastermind"
        },
        {
            "source": "SomeUUID000000000000000000000002",
            "target": "SomeUUID000000000000000000000003",
            "relation": "minion"
        }
    ]
}
```


### Deleting relations

If a deleted relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of the field is removed/updated accordingly.

Delete all relations of the type `enemy` from any source to any target:

```
DELETE /plone/@relations-catalog?relation=enemy
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

[...]