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

| Parameter | Description | Example |
|-----------|-------------|---------|
| `title` | Filter by title (case-insensitive substring match) | `title=my doc` |
| `path` | Filter by path (case-insensitive substring match) | `path=/plone/news` |
| `portal_type` | Filter by content type | `portal_type=Document` |
| `date_from` | Filter by deletion date from (YYYY-MM-DD) | `date_from=2024-01-01` |
| `date_to` | Filter by deletion date to (YYYY-MM-DD) | `date_to=2024-12-31` |
| `deleted_by` | Filter by the user ID who deleted the item | `deleted_by=admin` |
| `has_subitems` | Filter items with (`true`) or without (`false`) children | `has_subitems=true` |
| `language` | Filter by language code | `language=it` |
| `review_state` | Filter by workflow state | `review_state=published` |
| `sort_on` | Sort field: `title`, `portal_type`, `path`, `size`, `deletion_date`, `review_state` | `sort_on=title` |
| `sort_order` | Sort direction: `ascending` or `descending` (default) | `sort_order=ascending` |

### Batching

The API supports standard Plone REST API batching parameters (`b_start`, `b_size`).

#### Example with filtering and sorting

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_get_filtered.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_get_filtered.resp
:language: http
```

## Get individual item from recycle bin

To retrieve detailed information about a specific item in the recycle bin, including its children, send a `GET` request to `@recyclebin/{item_id}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_get_item.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_get_item.resp
:language: http
```

## Restore an item from the recycle bin

An item can be restored to its original location by issuing a `POST` to `@recyclebin/{item_id}/restore`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_restore.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_restore.resp
:language: http
```

### Restore to a specific location

Pass a `target_path` in the request body to restore the item to a different folder:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_restore_target.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_restore_target.resp
:language: http
```

## Purge a specific item from the recycle bin

To permanently delete a specific item, send a `DELETE` request to `@recyclebin/{item_id}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_item.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_item.resp
:language: http
```

## Empty the entire recycle bin

To permanently delete all items, send a `DELETE` request to `@recyclebin`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_all.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/recyclebin_purge_all.resp
:language: http
```
