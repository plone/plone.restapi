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

The `b_start` parameter defines the first item of the batch::

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


The `b_size` parameter is optional and the default value is `0`.

Batch Size (b_size)
^^^^^^^^^^^^^^^^^^^

The `b_size` parameter defines the number of elements a single batch returns:: 

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

The parameter is optional. And the default value is `25`.


Sort on
^^^^^^^

The `sort_on` parameter defines the field that is used to sort the returned search results::

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

The `sort_on` parameter is optional. The default value is `None`.

Sort Order
^^^^^^^^^^

The `sort_order` parameter defines the sort order when the `sort_on` field has been set::

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

The `sort_order` parameter is optional. The default value is `ascending`.

The sort_order can be either ‘ascending’ or ‘descending’, where ‘ascending’ means from A to Z for a text field. ‘reverse’ is an alias equivalent to ‘descending’.


Limit
^^^^^

Querystring Query with limit parameter::

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

The `limit` parameter is optional. The default value is `1000`.


Query
-----

The `query` parameter is a list that contains an arbitrary number of `filters`::


  {
    "query": [
      {
        'i': 'Title',
        'o': 'plone.app.querystring.operation.string.is',
        'v': 'Welcome to Plone',
      }
    ]
  }

A `filter` always contains three values:

* `ì`: the index of the filter (the name of the field this filter is applied to)
* `o`: the operator of the filter (the operator, a full list can be found here: https://github.com/plone/plone.app.querystring/blob/master/plone/app/querystring/profiles/default/registry.xml)
* `v`: the value of the filter (this highly depends on the index, for a text index, this is a string, for a date index this might be a date range)

The following type of filters are available:

* Metadata filters
* Date filters
* Text Filters

Metadata Filters
^^^^^^^^^^^^^^^^

Creator
,,,,,,,

The creator of the content object.

You can either set the currently logged in user::

  {
    "query":[
      {
        "i":"Creator",
        "o":"plone.app.querystring.operation.string.currentUser",
        "v":""
      }
    ],
  }

or set a username::

  {
    "query":[
      {
        "i":"Creator",
        "o":"plone.app.querystring.operation.selection.any",
        "v":["noam"]
      }
    ]
  }

Shortname
´´´´´´´´´

Shortname (the id of the object that is shown as last part of the URL)::

  {
    "query":[
      {
        "i":"getId",
        "o":"plone.app.querystring.operation.string.is",
        "v":"hero"
      }
    ]
  }

Location
,,,,,,,,

Location is the path of the content object on the site. You can either set three kind of paths.

The absolute path (from the portal root)::

  {
    "query":[
      {
        "i":"path",
        "o":"plone.app.querystring.operation.string.absolutePath",
        "v":"/my-content-object"
      }
    ]
  }

The relative path (relative from the current object)::

  {
    "query":[
      {
        "i":"path",
        "o":"plone.app.querystring.operation.string.relativePath",
        "v":"../my-content-object"
      }
    ]
  }

The navigation path::

  {
    "query":[
      {
        "i":"path",
        "o":"plone.app.querystring.operation.string.path",
        "v":"/hero"
      }
    ]
  }

The path can be stored computed::

  {
    "query": [
      {
        'i': 'path',
        'o': 'plone.app.querystring.operation.string.path',
        'v': '00000000000000001',
      }
    ]
  }

The path can contain a depth parameter (that is separated with a "::")::

  {
    "query": [
      {
        'i': 'path',
        'o': 'plone.app.querystring.operation.string.path',
        'v': '/my-content-object::2',
      }
    ]
  }

Type
,,,,

Filter by portal type::

  {
    "query": [
      {
        "i": "portal_type",
        "o": "plone.app.querystring.operation.selection.any",
        "v": ["Document"],
      }
    ]
  }

Review State
,,,,,,,,,,,,

Filter results by review state::

  {
    "query":[
      {
        "i":"review_state",
        "o":"plone.app.querystring.operation.selection.any",
        "v":["published"]
      }
    ]
  }


Show Inactive
,,,,,,,,,,,,,

Show inactive will return content objects that is expired for a given role::

  {
    "query":[
      {
        "i":"show_inactive",
        "o":"plone.app.querystring.operation.string.showInactive",
        "v":["Owner"]
      }
    ]
  }

Text Filters
^^^^^^^^^^^^

Description
,,,,,,,,,,,

Filter content that contains a term in the Description field::

  {
    "query":[
      {
        "i":"Description",
        "o":"plone.app.querystring.operation.string.contains",
        "v":"Noam"
      }
    ]
  }

Searchable Text
,,,,,,,,,,,,,,,

Filter content that contains a term in the SearchableText (all searchable fields in the catalog)::

  {
    "query":[
      {
        "i":"SearchableText",
        "o":"plone.app.querystring.operation.string.contains",
        "v":"Noam"
      }
    ]
  }

Tag
,,,

Filter by a tag (subjects field)::

  {
    "query":[
      {
        "i":"Subject",
        "o":"plone.app.querystring.operation.selection.any",
        "v":["Astrophysics"]
      }
    ]
  }


Title
,,,,,

Filter by exact Title match::

  "query": [
    {
      'i': 'Title',
      'o': 'plone.app.querystring.operation.string.is',
      'v': 'Welcome to Plone',
    }
  ]

Date Filters
^^^^^^^^^^^^

Creation Date
,,,,,,,,,,,,,

Filter by creation date::

  {
    "query":[
      {
        "i": "created",
        "o": "plone.app.querystring.operation.date.lessThan",
        "v": "2021-11-11"
      }
    ]
  }

Effective Date
,,,,,,,,,,,,,,

Filter by effective date::

  {
    "query":[
      {
        "i": "effective",
        "o": "plone.app.querystring.operation.date.largerThan",
        "v": "2021-11-11"
        }
      }
    ]
  }

Event end date
,,,,,,,,,,,,,,

Filter by event end date::

  {
    "query":[
      {
        "i": "end",
        "o": "plone.app.querystring.operation.date.lessThan",
        "v":"2021-11-04"
      }
    ]
  }

Event start date
,,,,,,,,,,,,,,,,

Filter by event start date::

  {
    "query":[
      {
        "i": "end",
        "o": "plone.app.querystring.operation.date.lessThan",
        "v":"2021-11-04"
      }
    ]
  }

Expiration date
,,,,,,,,,,,,,,,

Filter by expiration date::

  {
    "query":[
      {
        "i": "expires",
        "o": "plone.app.querystring.operation.date.largerThan",
        "v": "2021-11-11"
        }
      }
    ]
  }

Modification date
,,,,,,,,,,,,,,,,,

Filter by modification date::

  {
    "query":[
      {
        "i": "modified",
        "o": "plone.app.querystring.operation.date.largerThan",
        "v": "2021-11-11"
        }
      }
    ]
  }
