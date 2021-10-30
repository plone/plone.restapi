Querystring Search
==================

The ``@querystring-search`` endpoint returns search results that can be filtered on search criteria.

Call the ``/@querystring-search`` endpoint with a ``POST`` request and a query in the request body:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/querystringsearch_post.req

The server will respond with the results that are filtered based on the query you provided:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/querystringsearch_post.resp
   :language: http

Parameters the endpoint will accept:

  - ``query`` (plone.app.querystring query, required)
  - ``b_start`` (integer, batch start)
  - ``b_size`` (integer, batch size)
  - ``sort_on`` (string, field that results will be sorted on)
  - ``sort_order`` : ``"ascending"``, ``"descending"`` (string)
  - ``limit`` (integer, limits the number of returned results)
  - ``fullobjects`` : ``"true"``, ``"false``" (boolean, if true the return the full objects instead of just the summary serialization)

Query Parameters
----------------

Sort on
^^^^^^^

  {
    "sort_on": "sortable_title",
    "query": [
      {
        'i': 'Title',
        'o': 'plone.app.querystring.operation.string.is',
        'v': 'Welcome to Plone',
      }
    ]
  }

Sort Order
^^^^^^^^^^

Querystring Query with sort on and sort_order:

  {
    "sort_on": "sortable_title",
    "sort_order": "reverse",
    "query": [
      {
        'i': 'Title',
        'o': 'plone.app.querystring.operation.string.is',
        'v': 'Welcome to Plone',
      }
    ]
  }


Query Filters
-------------

The following filters are available.

Metadata Filters
^^^^^^^^^^^^^^^^

Creator
,,,,,,,

The creator of the content object, options: "currently logged in user", user fullname).

Shortname
´´´´´´´´´

Shortname (the id of the object that is shown as last part of the URL)

Location
,,,,,,,,

Location is the path of the content object on the site, e.g. /).

Filter by 'path':

Querystring Query with 'path':

  "query": [
    {
      'i': 'path',
      'o': 'plone.app.querystring.operation.string.path',
      'v': '/foo',
    }
  ]

The path can be stored computed:
            
  "query": [
    {
      'i': 'path',
      'o': 'plone.app.querystring.operation.string.path',
      'v': '00000000000000001',
    }
  ]

The path can contain a depth parameter (that is separated with a "::"):

  "query": [
    {
      'i': 'path',
      'o': 'plone.app.querystring.operation.string.path',
      'v': '/foo::2',
    }
  ]


Type
,,,,

Filter by portal type:

  "query": [
    {
      "i": "portal_type",
      "o": "plone.app.querystring.operation.selection.any",
      "v": ["Document"],
    }
  ]

Review State
,,,,,,,,,,,,


Show Inactive
,,,,,,,,,,,,,


Text Filters
^^^^^^^^^^^^

Description
,,,,,,,,,,,

Searchable Text
,,,,,,,,,,,,,,,

Tag
,,,


Title
,,,,,

Filter by exact Title match:

  "query": [
    {
      'i': 'Title',
      'o': 'plone.app.querystring.operation.string.is',
      'v': 'Welcome to Plone',
    }
  ]

Date Filters
^^^^^^^^^^^^

- Creation Date
- Effective Date
- Event end date
- Expiration date
- Modification date
- Event start date








Querystring query with multiple 'path' parameters:

    data_1 = {
        'i': 'path',
        'o': 'plone.app.querystring.operation.string.path',
        'v': '/foo',
    }
    data_2 = {
        'i': 'path',
        'o': 'plone.app.querystring.operation.string.path',
        'v': '/bar',
    }

  
Querystring Query with sort on:


