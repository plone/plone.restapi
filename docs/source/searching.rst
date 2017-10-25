Search
======

Content in a Plone site can be searched for by invoking the ``/@search`` endpoint on any context:

.. code-block:: http

    GET /plone/@search HTTP/1.1
    Accept: application/json

A search is **contextual** by default, i.e. it is bound to a specific collection and searches within that collection and any sub-collections.

Since a Plone site is also a collection, we therefore have a global search (by invoking the ``/@search`` endpoint on the site root) and contextual searches (by invoking that endpoint on any other context) all using the same pattern.

In terms of the resulting catalog query this means that, by default, a search will be constrained by the path to the context it's invoked on, unless you explicitly supply your own ``path`` query.

Search results are represented similar to collections:

..  http:example:: curl httpie python-requests
    :request: _json/search.req

.. literalinclude:: _json/search.resp
   :language: http

The default representation for search results is a summary that contains only the most basic information.
In order to return specific metadata columns, see the documentation of the ``metadata_fields`` parameter below.

.. note::
        Search results results will be **batched** if the size of the
        resultset exceeds the batch size. See :doc:`/batching` for more
        details on how to work with batched results.

.. warning::
        The @@search view or in Plone LiveSearch widget are coded in a way that the SearchableText parameter is expanded by including a * wildcard at the end.
        This is done in order to match also the partial results of the beginning of a search term(s).
        plone.restapi @search endpoint will not do that for you. You'll have to add it if you want to keep this feature.


Query format
------------

Queries and query-wide options (like ``sort_on``) are submitted as query string parameters to the ``/@search`` request:

.. code-block:: http

    GET /plone/@search?SearchableText=lorem HTTP/1.1

This is nearly identical to the way that queries are passed to the Plone ``@@search`` browser view, with only a few minor differences.

For general information on how to query the Plone catalog, please refer to the `Plone Documentation on Querying <http://docs.plone.org/develop/plone/searching_and_indexing/query.html>`_.

Query options
^^^^^^^^^^^^^

In case you want to supply query options to a query against a particular index, you'll need to flatten the corresponding query dictionary and use a dotted notation to indicate nesting.

For example, to specify the ``depth`` query option for a path query, the original query as a Python dictionary would look like this::

    query = {'path': {'query': '/folder',
                      'depth': 2}}

This dictionary will need to be flattened in dotted notation in order to pass it in a query string:

.. code-block:: http

    GET /plone/@search?path.query=%2Ffolder&path.depth=2 HTTP/1.1

Again, this is very similar to how `Record Arguments <http://docs.zope.org/zope2/zdgbook/ObjectPublishing.html?highlight=record#record-arguments>`_ are parsed by ZPublisher, except that you can omit the ``:record`` suffix.


Data types in queries
^^^^^^^^^^^^^^^^^^^^^

Because HTTP query strings contain no information about data types, any query string parameter value ends up as a string in the Zope's request.
This means, that for values types that aren't string, these data types need to be reconstructed on the server side in plone.restapi.

For most index types and their query values and query options, plone.restapi can handle this for you.
If you pass it ``path.query=foo&path.depth=1``, it has the necessary knowledge about the ``ExtendedPathIndex``'s options to turn the string ``1`` for the ``depth`` argument back into an integer before passing the query on to the catalog.

However, certain index types (a ``FieldIndex`` for example) may take arbitrary data types as query values.
In that case, ``plone.restapi`` simply can't know what data type to cast your query value to, and you'll need to specify it using ZPublisher type hints:

.. code-block:: http

    GET /plone/@search?numeric_field=42:int HTTP/1.1
    Accept: application/json


Please refer to the `Documentation on Argument Conversion in ZPublisher <http://docs.zope.org/zope2/zdgbook/ObjectPublishing.html#argument-conversion>`_ for details.


Retrieving additional metadata
------------------------------

By default the results are represented as summaries that only contain the most basic information about the items, like their URL and title.
If you need to retrieve additional metadata columns, you can do so by specifying the additional column names in the ``metadata_fields`` parameter:

.. code-block:: http

    GET /plone/@search?SearchableText=lorem&metadata_fields=modified HTTP/1.1
    Accept: application/json

The metadata from those columns then will be included in the results.
In order to specify multiple columns, simply repeat the query string parameter once for every column name (the ``requests`` module will do this automatically for you if you pass it a list of values for a query string parameter).

In order to retrieve all metadata columns that the catalog knows about, use ``metadata_fields=_all``.


Retrieving full objects
-----------------------

If the data provided as metadata is not enough, you can retrieve search results as full serialized objects equivalent to what the resource GET request would produce.

You do so by specifying the ``fullobjects`` parameter:

.. code-block:: http

    GET /plone/@search?fullobjects&SearchableText=lorem HTTP/1.1
    Accept: application/json

.. warning::

    Be aware that this might induce performance issues when retrieving a lot of resources. Normally the search just serializes catalog brains, but with full objects we wake up all the returned objects.
