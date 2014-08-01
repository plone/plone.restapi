.. include:: /alert-noindex.rst

*********
Searching
*********

Search results can be viewed as *virtual collections*. The representation and some of the attributes exposed by search results are therefore similar to the ones we saw until now.

A search is always contextual, i.e. it is bound to a specific collection and searches within that collection and any sub-collections. Since a Plone site is also a collection, we therefore have a global search and contextual searches all exposed with the same pattern.

A search is discoverable via the ``@queries`` attribute within a collection's representation: this attribute provides the URI of the search and also a template describing on which indexes the filtering can be done.

Since a search is actually a read operation, ``GET`` is used::

  GET /++api++1/big-folder/@@search?SearchableText=page&effective=2014-05-01
  Host: nohost
  Accept: application/json



  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/big-folder/@@search?SearchableText=page&effective__from=2014-05-01",
    "@info": {
      "items_count": 20
    },
    "@data": {
      "SearchableText": "page",
      "effective__from": "2014-05-01"
    },
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
       "@next": "http://nohost/++api++1/big-folder/@@search?SearchableText=page&effective__from=2014-05-01&page=2:10",
       "@last": "http://nohost/++api++1/big-folder/@@search?SearchableText=page&effective__from=2014-05-01&page=2:10",
       "@all": "http://nohost/++api++1/big-folder/@@search?SearchableText=page&effective__from=2014-05-01&page=all"
    },
    "@error": null
  }
