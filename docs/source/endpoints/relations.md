---
myst:
  html_meta:
    "description": "Create, query, and delete relations between content items with the /@relations endpoint."
    "property=og:description": "Create, query, and delete relations between content items with the /@relations endpoint."
    "property=og:title": "Relations"
    "keywords": "Plone, plone.restapi, REST, API, relations, service, endpoint"
---

(restapi-relations-label)=

# Relations

Plone's relations represent binary relationships between content objects.

There are relations based on fields in a content type schema that are editable by users.
There are also relations without fields, such as `linkintegrity` or `working-copy`, that are created and deleted dynamically.
Every relation element has a source object, a target object, and the name of the relation.

Relations can be created, queried, and deleted by interacting through the `@relations` endpoint on the site root.

Reading relations with the `@relations` endpoint requires the `zope2.View` permission on the content object.  
Creating and deleting relations requires the respective permission on the content object.


(restapi-relations-getting-statistics-for-all-relations-label)=

## Getting statistics for all relations

The call without any parameters returns statistics on all existing relations the user has access to.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_catalog_get_stats.req
```


```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_catalog_get_stats.resp
:language: http
```


(restapi-relations-querying-relations-label)=

## Querying relations

<!-- TODO replace examples by examples querying path (not uid) -->

A query of relations must provide one single source, one single target or one single relationship.
Combinations are allowed.  
source and target are UIDs or paths.

Relations with sources or targets for which the user does not have the `View permission` are omitted from the results.

The relations are grouped by relation name, and the source and target are returned using the summarizer format.

---

Query relations of a **relation type**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.resp
:language: http
```

Query relations of a **source** object:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_source.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_source.resp
:language: http
```

Query relations by relation name and source:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_source_and_relation.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_source_and_relation.resp
:language: http
```

Query relations to a target:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_target.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_target.resp
:language: http
```


(restapi-relations-creating-relations-label)=

## Creating relations

Create a relation of type `<relation name>` from source to target.
Or create multiple relations in one POST request.

Creating a relation requires a source UUID, a target UUID, and the name of the relation.

If the relation is based on a `RelationChoice` or `RelationList` field of the source object, the value of that field is created or updated accordingly.

% TODO Response

---

Add relations:

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
            "target": "AnotherUUID000000000000000000000003",
            "relation": "relatedItems"
        }
    ]
}
```


(restapi-relations-deleting-relations-label)=

## Deleting relations

If a to be deleted relation is based on a `RelationChoice` or `RelationList` field on the source object, the value of the field is removed or updated accordingly.

% TODO Response

---

Delete all relations of the type `comprisesComponentPart` from any source to any target:

```
DELETE /plone/@relations?relation=comprisesComponentPart
```

Delete all relations outgoing from a certain item:

```
DELETE /plone/@relations?source=uuid1
```

Delete all relations to a certain item:

```
DELETE /plone/@relations?target=uuid1
```

Or delete the relations of type `comprisesComponentPart` to a target object:

```
DELETE /plone/@relations?relation=comprisesComponentPart&target=uuid1
```
