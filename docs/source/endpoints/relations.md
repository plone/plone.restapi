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

A single relation is defined by source, target and relation name.

Relations are either defined by content type schema fields or are of type `linkintegrity` or `working-copy`.

Relations based on fields of a content type schema are editable by users.

Relations `linkintegrity` (block text links to a Plone content object) and `working-copy` (working copy is enabled and the content object is a working copy) are not. They are created and deleted with links in text, respectively creating and deleting working copies.


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

Creating a relation requires a source, a target, and the name of the relation.  
Source and target can be UID or path.

If the relation is based on a `RelationChoice` or `RelationList` field of the source object, the value of that field is created or updated accordingly.

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

Relations can be deleted: either by relation name, all relations of an object, or all relations to a target.  
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

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/relations_del_relationname.resp
:language: http
```

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

