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

Parameters
----------

Batch Start (b_start)
^^^^^^^^^^^^^^^^^^^^^

The `b_start` parameter defines the first item of the batch.

````
{
  "b_start": "5",
  "query": [
    {
      'i': 'Title',
      'o': 'plone.app.querystring.operation.string.is',
      'v': 'Welcome to Plone',
    }
  ]
}
````

The `b_size` parameter is optional and the default value is `0`.

Batch Size (b_size)
^^^^^^^^^^^^^^^^^^^

The `b_size` parameter defines the number of elements a single batch returns: 

````
{
  "b_size": "5",
  "query": [
    {
      'i': 'Title',
      'o': 'plone.app.querystring.operation.string.is',
      'v': 'Welcome to Plone',
    }
  ]
}
````

The parameter is optional. And the default value is `25`.


Sort on
^^^^^^^

The `sort_on` parameter defines the field that is used to sort the returned search results:

````
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
````

The `sort_on` parameter is optional. The default value is `None`.

Sort Order
^^^^^^^^^^

The `sort_order` parameter defines the sort order when the `sort_on` field has been set:


````
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
````

The `sort_order` parameter is optional. The default value is `ascending`.

The sort_order can be either ‘ascending’ or ‘descending’, where ‘ascending’ means from A to Z for a text field. ‘reverse’ is an alias equivalent to ‘descending’.


Limit
^^^^^

Querystring Query with limit parameter:

````
{
  "limit": "10",
  "query": [
    {
      'i': 'Title',
      'o': 'plone.app.querystring.operation.string.is',
      'v': 'Welcome to Plone',
    }
  ]
}
````

The `limit` parameter is optional. The default value is `1000`.


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


