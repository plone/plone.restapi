---
html_meta:
  "description": "Relations between content items can be created, queried and deleted using the /@relations endpoint."
  "property=og:description": "Relations between content items can be created, queried and deleted using the /@relations endpoint."
  "property=og:title": "Relations"
  "keywords": "Plone, plone.restapi, REST, API, Relations"
---

# Relations

Relations allow to model relationships between objects without using links or a hierarchy.
There are relations based on fields in content-type schema that are editable by users.
There are also relations without fields (e.g. linkintegrity or working-copy) that are created and deleted dynamically.
Every relation has a source object, a target object and the name of the relation.

Relations can be created, queried and deleted by interacting through the `@relations` endpoint.

Reading relations requires the `zope2.View` permission on both content objects.
Creating and deleting relations requires the `cmf.ModifyContent` permission on the content objects.


## Listing relations

By default outgoing relations are listed.
Alternatively you can query for incoming relations.
Optionally you can filter by relationship.

```{todo}
Do we want to support only the use-case ob accessing relations on the context or allow a query for all kinds of relations like plone.api does.

IMHO that would require a endpoint on the portal, e.g.

``/plone/@relations-query?source=uuid1&target=uuid2&relationship=foo``

Reusing /@relations on the portal for that would disallow managing the relations for the Dexterity site-root object (there are some issues with that still though...).

```

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

```{literalinclude} ../../src/plone/restapi/tests/http-examples/relations_relationname_get.resp
:language: http
```

Reading incoming relations for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_backrelations_get.req
```

Example response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/relations_backrelations_get.resp
:language: http
```

Reading incoming relations of a certain type for a content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_backrelations_relationname_get.req
```

Example response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/relations_backrelations_relationname_get.resp
:language: http
```


## Creating relations

You can create all kinds of relations between objects and query for them later.
If the relation you create is based on a `RelationChoice` or `RelationList` field on the source object, the value of that field is created/updated accordingly.

Adding a relation:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_post.req
```

Example response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/relations_post.resp
:language: http
```

Add multiple relations:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/relations_multiple_post.req
```

Example response:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/relations_multiple_post.resp
:language: http
```


## Deleting relations

In order to delete relation(s), you must provide either source, target, or relationship.
You can mix and match.

Delete all relations from this object to any target

```
DELETE /plone/test-document/@relations HTTP/1.1
```

Delete all relations from any source to this object

```
DELETE /plone/test-document/@relations?backrelations=1 HTTP/1.1
```

Delete relations with name "friend" from this object to any target

```
DELETE /plone/test-document/@relations?relation=friend HTTP/1.1
```

Delete relations with name "uncle" from any source to this object

```
DELETE /plone/test-document/@relations?backrelations=1&relation=uncle HTTP/1.1
```

Delete relations with name "enemy" from any source to any target

```
DELETE /plone/@manage-relations?relation=enemy HTTP/1.1
```

If a deleted relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of the field is removed/updated accordingly.
