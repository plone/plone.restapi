==============================================================================
Collections and Elements
==============================================================================

REST Resources
==============

A resource (in REST terminology) is anything important enough to have been given its own URL. A resource can be a piece of data, a physical object, or an abstract concept — anything at all. All that matters is that it has a URL and the representation — the document the client receives when it sends a GET request to the URL.

Therefore, in Plone any content object (a document, a folder, etc.) can be considered to be a resource.

A collection (in REST terminology) is a special kind of resource. It exists mainly to group other resources together. Its representation focuses on links to other resources, though it may al so include snippets from the representations of those other resources (rr even the full representations).

Therefore, any folderish object in Plone can be considered to be a collection (including Plone "collections" and the portal root).

From now on we will call folderish objects "collections" and non-folderish objects "elements".

Elements
========

This could be the JSON representation of a document in Plone::

  {
    "document":
    {
      "version" : "1.0",
      "href" : "http://www.plone.org/++api++v1/json/front-page",
      "data" : [
        {"name": "title", "value": "Welcome to Plone"},
        {"name": "description", "value": "Plone is an Open Source CMS."},
        {"name": "text", "value": "<p>Plone rocks!</p>"},
        {"name": "portal_type", "value": "Document"},
        {"name": "created", "value": "2013-04-22T05:33:58.930Z"}
      ],
    }
  }


Collections
===========

As a starting point we will use the "Collection+JSON" Document Format defined here:

  http://amundsen.com/media-types/collection/format/


Portal Root
-----------

Example representation of the Plone portal root object that contains three items (Front-Page, News, Events)::

  {
    "collection":
    {
      "version" : "1.0",
      "href" : "http://www.plone.org/++api++v1/json/",
      "items" : [
        {
          "href" : "http://www.plone.org/++api++v1/json/front-page/",
          "data" : [
            {"name": "title", "value": "Welcome to Plone"},
            {"name": "description", "value": "Plone is an Open Source CMS."},
            {"name": "text", "value": "<p>Plone rocks!</p>"},
            {"name": "portal_type", "value": "Document"},
            {"name": "created", "value": "2013-04-22T05:33:58.930Z"}
          ],
          "links" : []
        },
        {
          "href" : "http://www.plone.org/++api++v1/json/news/",
          "data" : [
            {"name": "title", "value": "News"},
            {"name": "description", "value": "A news folder."},
            {"name": "text", "value": "<p>This is a news folder.</p>"},
            {"name": "portal_type", "value": "Folder"},
            {"name": "created", "value": "2013-04-22T05:33:58.930Z"}
          ],
          "links" : []
        },
        {
          "href" : "http://www.plone.org/++api++v1/json/events/",
          "data" : [
            {"name": "title", "value": "Events"},
            {"name": "description", "value": "An events folder."},
            {"name": "text", "value": "<p>This is an events folder.</p>"},
            {"name": "portal_type", "value": "Folder"},
            {"name": "created", "value": "2013-04-22T05:33:58.930Z"}
          ],
          "links" : [
            {"rel": "next", "href": "/events?page=2"},
            {"rel": "previous", "href": "/events?page=0"},
            {"rel": "first", "href": "/events?page=1"},
            {"rel": "last", "href": "/events?page=5"}
          ]
        },
      ],
      "queries" : [
        {
          "href" : "/++api++v1/json/search",
          "rel" : "search",
          "prompt" : "Search the website",
          "data": [
            {
              "name": "SearchableText", "value" : "",
              "name": "effective", "value": "",
            }
          ]
        }
      ],
      "template" : {
        "data" : [
          {
            "prompt" : "Title of the content object",
            "name" : "title",
            "value" : ""
          },
          {
            "prompt" : "Portal Type of the content object",
            "name" : "portal_type",
            "value" : ""
          },
        ]
      },
      {
        "error": {
          "title" : "ValueError",
          "code" : "ErrorCode",
          "message" : "Value Error"
        }
      }
    }
  }

The collection type contains the following elements::

  {
    "collection" :
    {
      "version" : "1.0",
      "href" : URI,
      "items" : [ARRAY],
      "links" : [ARRAY],
      "queries" : [ARRAY],
      "template" : {OBJECT},
      "error" : {OBJECT}
    }
  }

* version: API version number
* href: A permanent link to the collection itself. (full url?)
* items: Links to the members of the collection, and partial representations of them. (brains?)
* links: Links to other resources related to the collection (lead image, author, etc.).
* queries: Hypermedia controls for searching the collection.
* template: A hypermedia control for adding a new item to the collection.
* error: The error object contains additional information on the latest error condition reported by the server. (This is optional)


Collection Transitions
======================

The REST HATEOAS (Hypermedia as the engine of application state) principle states that:

  Clients make state transitions only through actions that are dynamically identified within hypermedia by the server (e.g., by hyperlinks within hypertext). Except for simple fixed entry points to the application, a client does not assume that any particular action is available for any particular resources beyond those described in representations previously received from the server.

We will now briefly outline the basic collection state transitions.


Reading Collections
-------------------

A GET request on a resource URI returns a HTTP 200 (OK) code with a collection
represented as JSON object::

  *** REQUEST ***
  GET /my-collection/ HTTP/1.1
  Host: www.plone.org
  Accept: application/vnd.Collection+JSON

  *** RESPONSE ***
  200 OK HTTP/1.1
  Content-Type: application/vnd.Collection+JSON
  Content-Length: xxx
  {
    "collection":
      ...
      "template" : {
        "data" : [
          {
            "name" : "title",
            "value" : ""
          },
          {
            "name" : "portal_type",
            "value" : ""
          },
        ]
      },
    }
  }

The collection contains a "template" section providing all the necessary information to add a new element to the collection.


Add Element to an existing collection
-------------------------------------

Doing a POST request on a collection adds an item to the collection. The GET request on the collection contained a template section that tells the client which params need to be provided in order to create a new item::

  *** REQUEST ***
  POST /my-collection/ HTTP/1.1
  Host: www.plone.org
  Content-Type: application/vnd.Collection
  {
    "template": {
      "data": [
        {
          "name" : "title",
          "value" : "Document 1"
        },
        {
          "name" : "portal_type",
          "value" : "Document"
        }
      ]
    }
  }

The server responds with a HTTP 201 code and a location header containing the new resource URI of the object that has just been created::

  *** RESPONSE ***
  201 Created HTTP/1.1
  Location: http://www.plone.org/my-collection/document-1


Reading an item
---------------

The representation of an element can be retrieved with a GET request on the URI::

  *** REQUEST ***
  GET /my-collection/document-1 HTTP/1.1
  Host: www.plone.org
  Accept: application/vnd.Collection+JSON

The server responds with a 200 (OK) code and the collection as JSON in the body::

  *** RESPONSE ***
  200 OK HTTP/1.1
  Content-Type: application/vnd.Collection+JSON
  Content-Length: xxx
  { "collection" : { "href" : "...", "items" [ { "href" : "...", "data" : [...].} } }


Updating an item
----------------

An element can be updated by doing a PUT request on its URI::

  *** REQUEST ***
  PUT /my-collection/ HTTP/1.1
  Host: www.plone.org
  Content-Type: application/vnd.Collection+JSON
  { "template" : { "data" : [ ...] } }

The server responds with a 200 (OK) HTTP code if the update has been successful::

  *** RESPONSE ***
  200 OK HTTP/1.1


Deleting an element
-------------------

An element can be deleted by doing a DELETE request on its URI::

  *** REQUEST ***
  DELETE /my-collection/ HTTP/1.1
  Host: www.plone.org

The server will respond with a 204 (NO CONTENT) HTTP code::

  *** RESPONSE ***
  204 No Content HTTP/1.1
