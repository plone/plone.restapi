# Recycle Bin

The Recycle Bin REST API provides endpoints to interact with the Plone Recycle Bin functionality.

## List recycle bin contents

To list all items in the recycle bin, send a GET request to the `@recyclebin` endpoint:

```http-example
GET /@recyclebin HTTP/1.1
Accept: application/json
```

Response:

```json
{
  "@id": "http://localhost:8080/Plone/@recyclebin",
  "items": [
    {
      "@id": "http://localhost:8080/Plone/@recyclebin/6d6d626f-8c85-4f22-8747-adb979bbe3b1",
      "id": "document-1",
      "title": "My Document",
      "type": "Document",
      "path": "/Plone/folder/document-1",
      "parent_path": "/Plone/folder",
      "deletion_date": "2025-04-27T10:30:45.123456",
      "size": 1024,
      "recycle_id": "6d6d626f-8c85-4f22-8747-adb979bbe3b1",
      "actions": {
        "restore": "http://localhost:8080/Plone/@recyclebin/6d6d626f-8c85-4f22-8747-adb979bbe3b1/restore",
        "purge": "http://localhost:8080/Plone/@recyclebin/6d6d626f-8c85-4f22-8747-adb979bbe3b1"
      }
    }
  ],
  "items_total": 1
}
```

## Restore an item from the recycle bin

To restore an item from the recycle bin, send a POST request to the `@recyclebin/{item_id}/restore` endpoint:

```http-example
POST /@recyclebin/6d6d626f-8c85-4f22-8747-adb979bbe3b1/restore HTTP/1.1
Accept: application/json
Content-Type: application/json
```

You can optionally specify a target path to restore to by including it in the request body:

```json
{
  "target_path": "/Plone/another-folder"
}
```

Response:

```json
{
  "status": "success",
  "message": "Item document-1 restored successfully",
  "restored_item": {
    "@id": "http://localhost:8080/Plone/document-1",
    "id": "document-1",
    "title": "My Document",
    "type": "Document"
  }
}
```

## Purge an item from the recycle bin

To permanently delete an item from the recycle bin, send a POST request to the `@recyclebin-purge` endpoint:

```http-example
POST /@recyclebin-purge HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "item_id": "6d6d626f-8c85-4f22-8747-adb979bbe3b1"
}
```

Response:

```json
{
  "status": "success",
  "message": "Item document-1 purged successfully"
}
```

## Purge all items from the recycle bin

To purge all items from the recycle bin:

```http-example
POST /@recyclebin-purge HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "purge_all": true
}
```

Response:

```json
{
  "status": "success",
  "purged_count": 5,
  "message": "Purged 5 items from recycle bin"
}
```

## Purge expired items from the recycle bin

To purge only expired items (based on the retention period):

```http-example
POST /@recyclebin-purge HTTP/1.1
Accept: application/json
Content-Type: application/json

{
  "purge_expired": true
}
```

Response:

```json
{
  "status": "success",
  "purged_count": 2,
  "message": "Purged 2 expired items from recycle bin"
}
```
