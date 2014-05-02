.. include:: alert-noindex.rst

Collections
***********

A resource (in REST terminology) is anything important enough to have been given its own URL. Therefore a resource is a piece of data: all that matters is that it has a URL and a representation, which is what the client receives when it sends a ``GET`` request to the URL.

Therefore, in Plone any content object (a document, a folder, etc.) is a resource.

A collection (in REST terminology) is a special kind of resource. It exists mainly to group other resources together. Its representation focuses on links to other resources, though it may also include snippets from the representations of those other resources (even the full representations).

Therefore, any folderish object in Plone can be considered to be a collection (including Plone "collections" and the portal root).

From now on we will call folderish objects "collections" and non-folderish objects "elements".

Elements
========

This is the JSON representation of the front page in Plone (and hence of any page in Plone)::

  {
    "@href": "http://nohost/++api++1/front-page",
    "@info": {
      "portal_type": {
        "@href": "http://http://nohost/++api++1/++globals++types/Page",
        "@info": {
          "id": "Page"
        }
      },
      "created": "2014-04-22T05:33:58.930Z"
    },
    "@actions": {
      "workflow": {
        "@href": "http://http://nohost/++api++1/front-page/++actions++workflow/",
        "@template": {
           "type": {
             "@type": "string",
             "@choices": [
                "retract",
                "hide"
             ]
           }
        }
      }
    },
    "@data": {
      "title": "Welcome to Plone",
      "description": "Plone is an Open Source CMS.",
      "text": "<p>Plone rocks!</p>",
      "allow_discussion": null,
      "exclude_from_navigation": false,
      "table_of_contents": false,
      "tags": [],
      "language": null,
      "related_items": [],
      "effective": null,
      "expires": null,
      "creator": {
        "@href": "http://http://nohost/++api++1/++globals++users/admin"
        "@info": {
          "id": "admin"
        }
      },
      "contributors": [],
      "rights": ""
    }
  }


Portal root
===========

Example representation of the Plone portal root object that contains three items (Front-Page, News, Events)::

  GET http://nohost/++api++1/ HTTP/1.1
  Host: nohost
  Accept: application/json



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/",
    "@items": [
      {
        "@href": "http://nohost/++api++1/front-page/",
        "@data": {
          "title": "Welcome to Plone"
        },
        "@info": {
          "portal_type": {
            "@href": "http://http://nohost/++api++1/++globals++types/Page"
         },
         "created": "2014-04-22T05:33:58.930Z"
      },
      {
        "@href": "http://nohost/++api++1/front-page/news",
        "@data": {
          "title": "News"
        },
        "@info": {
          "portal_type": {
            "@href": "http://http://nohost/++api++1/++globals++types/Collection"
         },
         "created": "2014-04-22T05:33:58.930Z"
      },
      {
        "@href": "http://nohost/++api++1/front-page/events",
        "@data": {
          "title": "Events"
        },
        "@info": {
          "portal_type": {
            "@href": "http://http://nohost/++api++1/++globals++types/Collection"
         },
         "created": "2014-04-22T05:33:58.930Z"
      },
    ],
    "@queries": {
      "search": {
        "@href": "http://http://nohost/++api++1/@@search"
        "@template": {
           "SearchableText": {
             "@type": "string"
           },
           "effective": {
             "@type": "date"
           }
        }
      }
    },
    "@template" : {
    },
    "@error": null
  }

The collection hence has the following keywords:

@href
    A permanent link to the collection itself.

@elements
    Links to the members of the collection, and partial representations of them

@info
    Metadata related to the collection.

@queries
    Hypermedia controls for searching the collection.

@template
    A hypermedia control for adding a new item to the collection.

@error : optional
    The error object contains additional information on the latest error condition reported by the server (see :ref:`error-handling`)
