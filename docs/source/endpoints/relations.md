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

A single relation is defined by source, target, and relation name.

Relations are either defined by content type schema fields (`RelationChoice` or `RelationList`) or are of type `isReferencing` or `iterate-working-copy`.

- Relations based on fields of a content type schema are editable by users.
- Relations `isReferencing` (block text links to a Plone content object) and `iterate-working-copy` (working copy is enabled and the content object is a working copy) are not editable. They are created and deleted with links in text, respectively creating and deleting working copies.

Relations can be created, queried, and deleted by interacting through the `@relations` endpoint on the site root.
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

Relations can be queried by one single source, one single target or one single relation type.
Combinations are allowed.  
The source and target must be either a UID or path.

Queried relations require `View` permission on source and target.
If the user lacks permission to access these relations, then they are omitted from the query results.

The relations are grouped by relation name, source, and target, and are provided in a summarized format.

---

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

Querying can be further refined by applying the `query_target` search parameter to restrict the source and / or target to 
- contain a search string. Address the endpoint with for example `/@relations?relation=comprisesComponentPart&query_target=wheel` 
- be located under a path. Address the endpoint with for example `/@relations?relation=comprisesComponentPart&query_target=/inside/garden` 

### Limit the results

Limit the number of results by `max` to for example at most 100 results by `/@relations?relation=comprisesComponentPart&source=/documents/doc-1&max=100`

### Only broken relations

Retrieve broken relations by querying with `onlyBroken`:

`/@relations?onlyBroken=true`

Which returns an Object like

```json
{
  "@id": "http://localhost:55001/plone/@relations?onlyBroken=true", 
  "items": {
    "relatedItems": [
      [
        "http://localhost:55001/plone/document-2", 
        ""
      ]
    ]
  }, 
  "items_total": {
    "relatedItems": 1
  }
}
```



(restapi-relations-creating-relations-label)=

## Creating relations

Relations can be created by providing a list of the source, target, and name of the relation.
The source and target must be either a UID or path.

If the relation is based on a `RelationChoice` or `RelationList` field of the source object, the value of the field is created or updated accordingly.

Add by **path**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post.resp
:language: http
```

Add by **UID**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post_with_uid.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post_with_uid.resp
:language: http
```

**Failure**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_post_failure.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_post_failure.resp
:language: http
```

(restapi-relations-deleting-relations-label)=

## Deleting relations

Relations can be deleted by relation name, source object, target object, or a combination of these.
Relations can also be deleted by providing a list of single relations.

If a deleted relation is based on a `RelationChoice` or `RelationList` field, the value of the field is removed or updated accordingly on the source object.

### Delete a list of single relations

by **path**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_path.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_path.resp
:language: http
```

by **UID**:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_uid.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_uid.resp
:language: http
```

**Failures** are listed in response:

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

<!-- Uncomment with https://github.com/plone/plone.api/pull/502 merged
```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_relationname.resp
:language: http
``` -->

### Delete relations by source

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_source.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_source.resp
:language: http
```

Delete relations by source UID or source path.

### Delete relations by target

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_target.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_target.resp
:language: http
```

Delete relations by target UID or target path.

### Delete relations by combination of source/target and relation name

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/relations_del_combi.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_combi.resp
:language: http
```


## Fix relations

Broken relations can be fixed by releasing and re-indexing them.
Rebuild relations by `@relations?rebuild=1`

In rare cases flushing the `intIds` is needed.
Rebuild relations with flushing the `intIds` by `@relations?rebuild=1&flush=1`.
Be careful and think well before flushing if your code relies on `intIds`.
