.. include:: /alert-noindex.rst

**********************
Collection Transitions
**********************

The REST :abbr:`HATEOAS (hypermedia as the engine of application state)` principle states that:

  Clients make state transitions only through actions that are dynamically identified within hypermedia by the server (e.g., by hyperlinks within hypertext). Except for simple fixed entry points to the application, a client does not assume that any particular action is available for any particular resources beyond those described in representations previously received from the server.

We will now briefly outline the basic collection state transitions.


Reading Collections
===================

A ``GET`` request on a resource URI returns a HTTP 200 (OK) code with a collection
represented as JSON object::

  GET /++api++1/my-folder/ HTTP/1.1
  Host: nohost
  Accept: application/json



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/my-folder",
    "@info": {
      "portal_type": {
        "@href": "http://nohost/++api++1/++globals++types/Folder",
        "@id": "Folder"
      },
      "created": "2014-04-22T05:33:58.930Z",
      "review_state": "private",
      "items_count": 2
    },
    "@data": {
      "short_name": "my-folder",
      "title": "My folder",
      "description": "Just a folder",
      "tags": [],
      "language": null,
      "related_items": [],
      "effective": null,
      "expires": null,
      "creator": {
        "@href": "http://nohost/++api++1/++globals++users/admin"
        "@info": {
          "id": "admin"
        }
      },
      "contributors": [],
      "rights": ""
      "allow_discussion": null,
      "exclude_from_navigation": false,
      "enable_next_previous": false
    },
    "@template": {
      "@href": "http://nohost/++api++1/++globals++types/Folder/@@template"
    },
    "@items": [
      {
        "@href": "http://nohost/++api++1/my-folder/my-page",
        "@data": {
          "title": "My page"
        },
        "@info": {
          "portal_type": {
            "@href": "http://nohost/++api++1/++globals++types/Page"
          },
          "created": "2014-04-22T05:33:58.930Z"
        }
      },
      {
        "@href": "http://nohost/++api++1/my-folder/another-page",
        "@data": {
          "title": "Another page"
        },
        "@info": {
          "portal_type": {
            "@href": "http://nohost/++api++1/++globals++types/Page"
          },
          "created": "2014-04-22T05:33:58.930Z"
        }
      }
    ],
    "@queries": {
      "search": {
        "@href": "http://nohost/++api++1/my-folder/@@search"
        "@template": {
           "SearchableText": {
             "@type": "string"
           },
           "effective__from": {
             "@type": "date"
           },
           "effective__to": {
             "@type": "date"
           }
        }
      }
    },
    "@actions": {
      "workflow": {
        "@href": "http://nohost/++api++1/my-folder/++actions++workflow/",
        "@template": {
           "type": {
             "@type": "string",
             "@choices": [
                "submit",
                "publish"
             ]
           }
        }
      }
    },
    "@item_templates": [
      {
        "@href": "http://nohost/++api++1/++globals++types/Page/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/News%20Item/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Link/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Image/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Folder/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/File/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Event/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Collection/@@template"
      }
    ],
    "@error": null
  }

.. _adding-an-element:

Adding an element
=================

Doing a ``POST`` request on a collection adds an item to the collection.

The ``GET`` request on the collection contained a ``@templates`` section with links to other parts of the API (see :doc:`/global-objects`) that tells the client which params need to be provided in order to create a new item.

The server replies with a ``201 Created`` status and the new URI in a ``Location`` header::

  POST /++api++1/my-folder/ HTTP/1.1
  Host: nohost
  Content-Type: application/json

  {
    "@info": {
      "portal_type": "Page"
    },
    "@data": {
      "title": "Yet another page",
      "description": null,
      "text": "<p>I've got a fever, and the only cure is <b>more</b> JSON!</p>"
    }
  }



  201 Created HTTP/1.1
  Location: http://nohost/++api++1/my-folder/yet-another-page/


Reading an element
==================

A ``GET`` request retrieves the representation of an element::

  GET /++api++1/my-folder/yet-another-page/ HTTP/1.1
  Host: nohost
  Accept: application/json



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/my-folder/yet-another-page/",
    "@info": {
      "portal_type": {
        "@href": "http://nohost/++api++1/++globals++types/Page",
        "@info": {
          "id": "Page"
        }
      },
      "created": "2014-04-22T05:33:58.930Z"
    },
    "@actions": {
      "workflow": {
        "@href": "http://nohost/++api++1/my-folder/yet-another-page/++actions++workflow/",
        "@template": {
           "type": {
             "@type": "string",
             "@choices": [
                "submit",
                "publish"
             ]
           }
        }
      }
    },
    "@data": {
      "short_name": "yet-another-page",
      "title": "Yet another page",
      "description": null,
      "text": "<p>I've got a fever, and the only cure is <b>more</b> JSON!</p>",
      "allow_discussion": null,
      "exclude_from_navigation": false,
      "table_of_contents": false,
      "tags": [],
      "language": null,
      "related_items": [],
      "effective": null,
      "expires": null,
      "creator": {
        "@href": "http://nohost/++api++1/++globals++users/admin"
        "@info": {
          "id": "admin"
        }
      },
      "contributors": [],
      "rights": ""
    },
    "@template": {
      "@href": "http://nohost/++api++1/++globals++types/Page/@@template"
    }
  }

.. _updating-an-element:

Updating an element
===================

To update the attributes appearing in ``@data`` inside the representation, the client uses a ``PATCH`` request.

The client doesn't need to supply all the attributes listed in the representation, those not listed in the request will be left as they are.

For example::

  PATCH /++api++1/my-folder/yet-another-page/ HTTP/1.1
  Host: nohost
  Content-Type: application/json

  {
    "@data": {
      "text": "<p>I've got <i>JSON</i>"
    }
  }



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/my-folder/yet-another-page/",
    "@info": {
      "portal_type": {
        "@href": "http://nohost/++api++1/++globals++types/Page",
        "@info": {
          "id": "Page"
        }
      },
      "created": "2014-04-22T05:33:58.930Z"
    },
    "@actions": {
      "workflow": {
        "@href": "http://nohost/++api++1/my-folder/yet-another-page/++actions++workflow/",
        "@template": {
           "type": {
             "@type": "string",
             "@choices": [
                "submit",
                "publish"
             ]
           }
        }
      }
    },
    "@data": {
      "short_name": "yet-another-page",
      "title": "Yet another page",
      "description": null,
      "text": "<p>I've got <i>JSON</i>",
      "allow_discussion": null,
      "exclude_from_navigation": false,
      "table_of_contents": false,
      "tags": [],
      "language": null,
      "related_items": [],
      "effective": null,
      "expires": null,
      "creator": {
        "@href": "http://nohost/++api++1/++globals++users/admin"
        "@info": {
          "id": "admin"
        }
      },
      "contributors": [],
      "rights": ""
    },
    "@template": {
      "@href": "http://nohost/++api++1/++globals++types/Page/@@template"
    }
  }

.. note::
   The client is limited to the attributes listed in ``@data``.
   This is not quite discoverable, but for trying and receiving an error.


Deleting an element
===================

To delete an element it is sufficient to send a ``DELETE`` request, to which the server will reply with a ``204 No Content`` code if succesful::

  DELETE /++api++1/my-folder/yet-another-page/ HTTP/1.1
  Host: nohost



  204 No Content HTTP/1.1


Replacing an element
====================

.. note::
   This is equivalent of doing a deletion and then adding a new element, although this is done in a single request and is therefore guaranteed to be transactional.

To entirely replace an existing element, a ``PUT`` request can be used. This doesn't work as we saw in :ref:`updating-an-element`, because the semantic of the request are similar to that of :ref:`adding-an-element`.

Let's see with an example::

  PUT /++api++1/my-folder/yet-another-page HTTP/1.1
  Host: nohost
  Content-Type: application/json

  {
    "@info": {
      "portal_type": "Folder"
    },
    "@data": {
      "title": "The URL lies!",
      "description": "Quite so, I'm a folder"
    }
  }



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/my-folder/yet-another-page/",
    "@info": {
      "portal_type": {
        "@href": "http://nohost/++api++1/++globals++types/Folder",
        "@id": "Folder"
      },
      "created": "2014-04-22T05:33:58.930Z",
      "items_count": 0
    },
    "@data": {
      "short_name": "yet-another-page",
      "title": "The URL lies!",
      "description": "Quite so, I'm a folder",
      "tags": [],
      "language": null,
      "related_items": [],
      "effective": null,
      "expires": null,
      "creator": {
        "@href": "http://nohost/++api++1/++globals++users/admin"
        "@info": {
          "id": "admin"
        }
      },
      "contributors": [],
      "rights": ""
      "allow_discussion": null,
      "exclude_from_navigation": false,
      "enable_next_previous": false
    },
    "@template": {
      "@href": "http://nohost/++api++1/++globals++types/Folder/@@template"
    }
    "@items": [],
    "@queries": {
      "search": {
        "@href": "http://nohost/++api++1/my-folder/yet-another-page/@@search"
        "@template": {
           "SearchableText": {
             "@type": "string"
           },
           "effective__from": {
             "@type": "date"
           },
           "effective__to": {
             "@type": "date"
           }
        }
      }
    },
    "@actions": {
      "workflow": {
        "@href": "http://nohost/++api++1/my-folder/yet-another-page/++actions++workflow/",
        "@template": {
           "type": {
             "@type": "string",
             "@choices": [
                "submit",
                "publish"
             ]
           }
        }
      }
    }
    "@item_templates": [
      {
        "@href": "http://nohost/++api++1/++globals++types/Page/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/News%20Item/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Link/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Image/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Folder/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/File/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Event/@@template"
      },
      {
        "@href": "http://nohost/++api++1/++globals++types/Collection/@@template"
      }
    ],
    "@error": null
  }

As we can see, we effectively substituted a page with a folder.
