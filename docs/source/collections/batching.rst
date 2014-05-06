.. include:: /alert-noindex.rst

********
Batching
********

Returning the whole objects contained in a collection might be problematic for a number of reasons:

 #. Forces the server to read all the content
 #. Might produce a heavy response (in terms of byte size)
 #. Might not interest the client (e.g. the client might be interested only in the collection data, and not its elements)

The REST way of solving this problem is through pagination.

Let's try to retrieve a big collection::

  GET /++api++1/big-folder/ HTTP/1.1
  Host: nohost
  Accept: application/json



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/big-folder",
    "@info": ...,
    "@data": ...,
    "@template": ...,
    "@items": [
      {
        "@href": "http://nohost/++api++1/big-folder/page-1",
        "@data": {
          "title": "Page 1"
        },
        "@info": {
          "portal_type": {
            "@href": "http://nohost/++api++1/++globals++types/Page"
          },
          "created": ...
        }
      },
      ...
    ],
    "@links": {
       "@next": "http://nohost/++api++1/big-folder?page=2:10",
       "@last": "http://nohost/++api++1/big-folder?page=5:10",
       "@all": "http://nohost/++api++1/big-folder?page=all"
    },
    "@queries": ...,
    "@actions": ...,
    "@item_templates": ...,
    "@error": null
  }

The catch here is the ``@links`` attribute that appears, which provides:

  #. A link to the next batch of contents (``@next``)
  #. A link to the last batch of contents (``@last``)
  #. A link to the previous batch of contents (``@prev``)
  #. A link to the first batch of contents (``@first``)
  #. A link to a batch containing all contents (``@all``)

You might have noticed that the response there was missing ``@prev`` and ``@first``: this is because the API will only provide links that are useful or valid (i.e. links pointing to the current page are not useful).

In a slight diversion to the *HATEOAS* principle, the paging mechanism allows for a non-discoverable customization of the page size in the format of the ``page`` argument: this is in fact composed by two numbers, the first being the page number itself, and the second the page size.
By combining this information with the ``item_count`` attributes within the ``@info`` parameter, a client should be able to construct a different kind of pagination (although it would have to assume things, which is contrary to the *HATEOAS* principle, hence making it a not-so-restful client).

If we try to get the next page we will obtain::

  GET /++api++1/big-folder/?page=2:10 HTTP/1.1
  Host: nohost
  Accept: application/json



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/big-folder",
    "@info": ...,
    "@data": ...,
    "@template": ...,
    "@items": [
      {
        "@href": "http://nohost/++api++1/big-folder/page-11",
        "@data": {
          "title": "Page 11"
        },
        "@info": {
          "portal_type": {
            "@href": "http://nohost/++api++1/++globals++types/Page"
          },
          "created": ...
        }
      },
      ...
    ],
    "@links": {
       "@first": "http://nohost/++api++1/big-folder",
       "@prev": "http://nohost/++api++1/big-folder",
       "@next": "http://nohost/++api++1/big-folder?page=3:10",
       "@last": "http://nohost/++api++1/big-folder?page=5:10",
       "@all": "http://nohost/++api++1/big-folder?page=all"
    },
    "@queries": ...,
    "@actions": ...,
    "@item_templates": ...,
    "@error": null
  }
