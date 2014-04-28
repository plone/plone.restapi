What’s a Collection?
--------------------

A collection is a special kind of resource. A resource is anything important enough to have been given its own URL. A resource can be a piece of data, a physical object, or an abstract concept — anything at all. All that matters is that it has a URL and the representation — the document the client receives when it sends a GET request to the URL.

A collection resource is a little more specific than that. It exists mainly to group other resources together. Its representation focuses on links to other resources, though it may also include snippets from the representations of those other resources. (Or even the full representations!)

(RESTful WEB APIs, p. 93)

Collection+JSON - Document Format:

http://amundsen.com/media-types/collection/format/

Collection-like objects in Plone:

* Portal Root
* Folderish Objects
* Collections


Portal Root
-----------

{
  "collection":
  {
    "version" : "1.0",
    "href" : "http://www.plone.org/++api++v1/",
    "items" : [
      {
        "href" : "http://www.plone.org/++api++v1/front-page/",
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
        "href" : "http://www.plone.org/++api++v1/news/",
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
        "href" : "http://www.plone.org/++api++v1/events/",
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
        "href" : "/api/search",
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
    }
  }
}

* href: A permanent link to the collection itself. (full url?)
* items: Links to the members of the collection, and partial representations of them. (brains?)
* links: Links to other resources related to the collection (lead image, author, etc.).
* queries: Hypermedia controls for searching the collection.
* template: A hypermedia control for adding a new item to the collection.

// sample collection object
{
  "collection" :
  {
    "version" : "1.0",
    "href" : URI,
    "links" : [ARRAY],
    "items" : [ARRAY],
    "queries" : [ARRAY],
    "template" : {OBJECT},
    "error" : {OBJECT}
  }
}


Document
--------

{
  "document":
  {
    "version" : "1.0",
    "href" : "http://www.plone.org/++api++v1/front-page",
    "data" : [
      {"name": "title", "value": "Welcome to Plone"},
      {"name": "description", "value": "Plone is an Open Source CMS."},
      {"name": "text", "value": "<p>Plone rocks!</p>"},
      {"name": "portal_type", "value": "Document"},
      {"name": "created", "value": "2013-04-22T05:33:58.930Z"}
    ],
  }
}

* GET: Get the representation of a resource.
* POST: Creates a new resource.
* PUT: Replace an existing resource.
* PATCH: Modify an existing resource.
* DELETE: Remove an existing resource.
