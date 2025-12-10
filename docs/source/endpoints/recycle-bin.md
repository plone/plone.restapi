---
myst:
  html_meta:
    "description": "The Recycle Bin REST API provides endpoints to interact with the Plone Recycle Bin functionality."
    "property=og:description": "The Recycle Bin REST API provides endpoints to interact with the Plone Recycle Bin functionality."
    "property=og:title": "Recycle Bin"
    "keywords": "Plone, plone.restapi, REST, API, Recycle Bin"
---

# Recycle Bin

The Recycle Bin REST API provides endpoints to interact with the Plone Recycle Bin functionality.

Reading or writing recycle bin data requires the `cmf.ManagePortal` permission.

## List recycle bin contents

A list of all items in the recycle bin can be retrieved by sending a `GET` request to the `@recyclebin` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_get.resp
:language: http
```

### Filtering and Sorting Parameters

The listing supports various query parameters for filtering and sorting:

- `search_query`: Search in title and path (case-insensitive)
- `filter_type`: Filter by content type (e.g., "Document", "Folder")
- `date_from`: Filter by deletion date from (YYYY-MM-DD format)
- `date_to`: Filter by deletion date to (YYYY-MM-DD format)
- `filter_deleted_by`: Filter by user who deleted the item
- `filter_has_subitems`: Filter items with/without children (`with_subitems`, `without_subitems`)
- `filter_language`: Filter by language code
- `filter_workflow_state`: Filter by workflow state
- `sort_by`: Sorting options:
  - `date_desc` (default) - Most recent first
  - `date_asc` - Oldest first
  - `title_asc` / `title_desc` - Alphabetical by title
  - `type_asc` / `type_desc` - By content type
  - `path_asc` / `path_desc` - By path
  - `size_asc` / `size_desc` - By size
  - `workflow_asc` / `workflow_desc` - By workflow state

### Batching

The API supports standard Plone REST API batching parameters:

- `b_start`: Starting position for batch
- `b_size`: Number of items per batch

#### Example with filtering and sorting

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_get_filtered.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_get_filtered.resp
:language: http
```

## Get individual item from recycle bin

To retrieve detailed information about a specific item in the recycle bin, send a GET request to `@recyclebin/{item_id}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_get_item.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_get_item.resp
:language: http
```

## Restore an item from the recycle bin

An item can be restored from the recycle bin by issuing a `POST` to the given URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_restore.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_restore.resp
:language: http
```

### Restore to specific target location

You can specify a target path to restore the item to a different location than its original:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_restore_target.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_restore_target.resp
:language: http
```

## Purge a specific item from the recycle bin

To permanently delete a specific item from the recycle bin, send a DELETE request to the `@recyclebin/{item_id}` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_item.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_item.resp
:language: http
```

## Empty the entire recycle bin

To permanently delete all items from the recycle bin, send a DELETE request to the `@recyclebin` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_all.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_all.resp
:language: http
```
