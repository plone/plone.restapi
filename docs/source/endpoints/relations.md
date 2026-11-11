---
myst:
  html_meta:
    "description": "Create, query, and delete relations between content items with the relations endpoint."
    "property=og:description": "Create, query, and delete relations between content items with the relations endpoint."
    "property=og:title": "Relations"
    "keywords": "Plone, plone.restapi, REST, API, relations, service, endpoint"
---

(restapi-relations-label)=

# Relations

Plone's relations represent binary relationships between content objects.

A single relation is defined by source, target, and relation name.

You can define relations either with content type schema fields `RelationChoice` or `RelationList`, or with types `isReferencing` or `iterate-working-copy`.

- Relations based on fields of a content type schema are editable by users.
- The relations `isReferencing` (block text links to a Plone content object) and `iterate-working-copy` (working copy is enabled and the content object is a working copy) are not editable.
  They are created and deleted with links in text, respectively creating and deleting working copies.

You can create, query, and delete relations by interacting through the `@relations` endpoint on the site root.
Querying relations with the `@relations` endpoint requires the `zope2.View` permission on both the source and target objects.
Therefore results include relations if and only if both the source and target are accessible by the querying user.
Creating and deleting relations requires `zope2.View` permission on the target object and `cmf.ModifyPortalContent` permission on the source object.

(restapi-relations-getting-statistics-for-all-relations-label)=

## Getting statistics for all relations

The call without any parameters returns statistics on all existing relations to which the user has access.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_catalog_get_stats.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_catalog_get_stats.resp
:language: http
```

(restapi-relations-querying-relations-label)=

## Querying relations

You can query relations by a single source, target, or relation type.
Combinations are allowed.
The source and target must be either a UID or path.

Queried relations require the `View` permission on the source and target.
If the user lacks permission to access these relations, then they are omitted from the query results.

The relations are grouped by relation name, source, and target, and are provided in a summarized format.


Query relations of a **relation type**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_relationname.resp
:language: http
```

Query relations of a **source** object by path:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_source_by_path.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_source_by_path.resp
:language: http
```

Query relations of a **source** object by UID:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_source_by_uid.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_source_by_uid.resp
:language: http
```

Query relations by **relation name and source**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_source_and_relation.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_source_and_relation.resp
:language: http
```

Query relations to a **target**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_get_target.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_get_target.resp
:language: http
```

### Refining

Querying can be further refined by applying the `query_target` search parameter to restrict the source or target to either contain a search string or be located under a path.

Search string example:

```
/@relations?relation=comprisesComponentPart&query_target=wheel
```

Path example:

```
/@relations?relation=comprisesComponentPart&query_target=/inside/garden
```

### Limit the results

Limit the number of results by `max` to, for example, at most 100 results:

```
/@relations?relation=comprisesComponentPart&source=/documents/doc-1&max=100
```

### Only broken relations

Retrieve items with broken relations by querying with `onlyBroken`:

```
/@relations?onlyBroken=true
```

This returns a JSON object, for example:

```json
{
  "@id": "http://localhost:55001/plone/@relations?onlyBroken=true",
  "relations": {
    "relatedItems": {
      "items": [
        "http://localhost:55001/plone/document-2",
      ],
      "items_total": 1
    }
  }
}
```


(restapi-relations-creating-relations-label)=

## Creating relations

You can create relations by providing a list of the source, target, and name of the relation.
The source and target must be either a UID or path.

If the relation is based on a `RelationChoice` or `RelationList` field of the source object, the value of the field is updated accordingly.

Create a relation by **path**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post.resp
:language: http
```

Create a relation by **UID**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post_with_uid.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post_with_uid.resp
:language: http
```

If either the source or target do not exist, then an attempt to create a relation will fail, and will return a `422 Unprocessable Entity` response.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post_failure.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post_failure.resp
:language: http
```

(restapi-relations-deleting-relations-label)=

## Deleting relations

You can delete relations by relation name, source object, target object, or a combination of these.
You can also delete relations by providing a list of relations.

If a deleted relation is based on a `RelationChoice` or `RelationList` field, the value of the field is removed or updated accordingly on the source object.

### Delete a list of relations

You can delete relations by either UID or path.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_path_uid.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_path_uid.resp
:language: http
```

If either the source or target do not exist, then an attempt to delete a relation will fail, and will return a `422 Unprocessable Entity` response.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_failure.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_failure.resp
:language: http
```

### Delete relations by relation name

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_relationname.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_relationname.resp
:language: http
```

### Delete relations by source

You can delete relations by either source UID or path.

The following example shows how to delete a relation by source path.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_source.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_source.resp
:language: http
```

### Delete relations by target

You can delete relations by either target UID or path.

The following example shows how to delete a relation by target path.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_target.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_target.resp
:language: http
```

### Delete relations by a combination of source, target, and relation name

You can delete relations by a combination of either any two of their relation name, source, and target, or a combination of all three.
In the following example, you would delete a relation by its relation name and target.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_combi.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_combi.resp
:language: http
```


## Fix relations

Broken relations can be fixed by releasing and re-indexing them.
A successfully fixed relation will return a `204 No Content` response.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_rebuild.req
```

In rare cases, you may need to flush the `intIds`.
You can rebuild relations by flushing the `intIds` with the following HTTP POST request.

```{warning}
If your code relies on `intIds`, you should take caution and think carefully before you flush them.
```


```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_rebuild_with_flush.req
```
