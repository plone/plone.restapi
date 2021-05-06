Working Copy
============

Plone has the "Working copy" feature provided by the core package ``plone.app.iterate``.
It allows the user to create a working copy of a (published or live) content object and
work with it until it's ready to be published without having to edit the original object.

This process has several steps of it's life cycle:

Check-out
---------

The user initiates the process and creates a "working copy" by "checking out" the content::

POST /plone/document/@workingcopy HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

and receives the response::

HTTP/1.1 201 Created
Content-Type: application/json
Location: http://localhost:55001/plone/working_copy_of_document

Get the working copy
--------------------

A working copy has been created and can be accessed querying the content::

GET /plone/document/@workingcopy HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

and receives the response::

HTTP/1.1 200 OK
Content-Type: application/json

{
  "@id": "http://localhost:55001/plone/working_copy_of_document",
}

the GET content of any object, also states the location of the working copy, if any (``working_copy``).

GET /plone/document HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

HTTP/1.1 200 OK
Content-Type: application/json

{
  "@components": {
    "actions": {
      "@id": "http://localhost:55001/plone/document/@actions"
    },
    "breadcrumbs": {
      "@id": "http://localhost:55001/plone/document/@breadcrumbs"
    },
    "contextnavigation": {
      "@id": "http://localhost:55001/plone/document/@contextnavigation"
    },
    "navigation": {
      "@id": "http://localhost:55001/plone/document/@navigation"
    },
    "types": {
      "@id": "http://localhost:55001/plone/document/@types"
    },
    "workflow": {
      "@id": "http://localhost:55001/plone/folder/my-document/@workflow"
    }
  },
  "@id": "http://localhost:55001/plone/folder/my-document",
  "@type": "Document",
  "UID": "SomeUUID000000000000000000000005",
  "allow_discussion": false,
  "changeNote": "",
  "contributors": [],
  "created": "1995-07-31T13:45:00",
  "creators": [
    "admin"
  ],
  "description": "",
  "effective": null,
  "exclude_from_nav": false,
  "expires": null,
  "id": "my-document",
  "is_folderish": false,
  "language": "",
  "layout": "document_view",
  "modified": "1995-07-31T17:30:00",
  "next_item": {},
  "parent": {
    "@id": "http://localhost:55001/plone/folder",
    "@type": "Folder",
    "description": "This is a folder with two documents",
    "review_state": "private",
    "title": "My Folder"
  },
  "previous_item": {
    "@id": "http://localhost:55001/plone/folder/doc2",
    "@type": "Document",
    "description": "",
    "title": "A document within a folder"
  },
  "relatedItems": [],
  "review_state": "private",
  "rights": "",
  "subjects": [],
  "table_of_contents": null,
  "text": null,
  "title": "My Document",
  "version": "current",
  "versioning_enabled": true
  working_copy: {
    "@id": "http://localhost:55001/plone/working_copy_of_document",
  }
}

the GET content of any a working copy also returns the original (``working_copy_of``)::

GET /plone/document HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

HTTP/1.1 200 OK
Content-Type: application/json

{
  "@components": {
    "actions": {
      "@id": "http://localhost:55001/plone/working_copy_of_document/@actions"
    },
    "breadcrumbs": {
      "@id": "http://localhost:55001/plone/working_copy_of_document/@breadcrumbs"
    },
    "contextnavigation": {
      "@id": "http://localhost:55001/plone/working_copy_of_document/@contextnavigation"
    },
    "navigation": {
      "@id": "http://localhost:55001/plone/working_copy_of_document/@navigation"
    },
    "types": {
      "@id": "http://localhost:55001/plone/working_copy_of_document/@types"
    },
    "workflow": {
      "@id": "http://localhost:55001/plone/working_copy_of_document/@workflow"
    }
  },
  "@id": "http://localhost:55001/plone/working_copy_of_document",
  "@type": "Document",
  "UID": "SomeUUID000000000000000000000005",
  "allow_discussion": false,
  "changeNote": "",
  "contributors": [],
  "created": "1995-07-31T13:45:00",
  "creators": [
    "admin"
  ],
  "description": "",
  "effective": null,
  "exclude_from_nav": false,
  "expires": null,
  "id": "my-document",
  "is_folderish": false,
  "language": "",
  "layout": "document_view",
  "modified": "1995-07-31T17:30:00",
  "next_item": {},
  "parent": {
    "@id": "http://localhost:55001/plone/folder",
    "@type": "Folder",
    "description": "This is a folder with two documents",
    "review_state": "private",
    "title": "My Folder"
  },
  "previous_item": {
    "@id": "http://localhost:55001/plone/folder/doc2",
    "@type": "Document",
    "description": "",
    "title": "A document within a folder"
  },
  "relatedItems": [],
  "review_state": "private",
  "rights": "",
  "subjects": [],
  "table_of_contents": null,
  "text": null,
  "title": "My Document",
  "version": "current",
  "versioning_enabled": true
  working_copy_of: {
    "@id": "http://localhost:55001/plone/document",
  }
}

Check-in
---------

Once the user has finished editing the working copy and wants to update the original
with the changes in there, or "check-in" the working copy.

PATCH /plone/document/@workingcopy HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

and receives the response::

HTTP/1.1 204 No Content

The working copy is deleted afterwards as a result of this process.

Delete the working copy (cancel check-out)
------------------------------------------

If you want to cancel the checkout and delete the working copy (in both the original and
the working copy)::

DELETE /plone/document/@workingcopy HTTP/1.1
Accept: application/json
Authorization: Basic YWRtaW46c2VjcmV0

and receives the response::

HTTP/1.1 204 No Content

When a working copy is deleted using the "normal" delete action, it also deletes the
relation and cancels the check-out, but that is handled by ``plone.app.iterate`` internals.
