Search
======

Content in a Plone site can be searched for by invoking the ``/@search`` endpoint on any context:

.. code-block:: http

    GET /plone/@search HTTP/1.1
    Accept: application/json

A search is **contextual** by default, i.e. it is bound to a specific context (a *collection* in HTTP REST terms) and searches within that collection and any sub-collections.

Since a Plone site is also a collection, we therefore have a global search (by invoking the ``/@search`` endpoint on the site root) and contextual searches (by invoking that endpoint on any other context) all using the same pattern.

In terms of the resulting catalog query this means that, by default, a search will be constrained by the path to the context it's invoked on, unless you explicitly supply your own ``path`` query.

Search results are represented similar to collections:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/search.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/search.resp
   :language: http

The default representation for search results is a summary that contains only the most basic information.
In order to return specific metadata columns, see the documentation of the ``metadata_fields`` parameter below.

.. note::
        A search invoked on a container will by default **include that container
        itself** as part of the search results. This is the same behavior as displayed by
        `ZCatalog <https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html>`_, which is used internally.
        If you add the query string
        parameter ``depth=1`` to your search, you will only get **immediate**
        children of the container, and the container itself also won't be part
        of the results. See the Plone docs on
        `searching for content within a folder <https://docs.plone.org/develop/plone/searching_and_indexing/query.html#searching-for-content-within-a-folder>`_
        for more details.

.. note::
        Search results will be **batched** if the size of the
        resultset exceeds the batch size. See :doc:`/batching` for more
        details on how to work with batched results.

.. warning::
        The @@search view or the Plone LiveSearch widget are coded in a way that the SearchableText parameter is expanded by including a * wildcard at the end.
        This is done in order to match also the partial results of the beginning of a search term(s).
        The plone.restapi @search endpoint will not do that for you. You'll have to add it if you want to keep this feature.

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

    query = {'path': {'query': '/folder1',
                      'depth': 2}}

This dictionary will need to be flattened in dotted notation in order to pass it in a query string:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/search_options.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/search_options.resp
   :language: http

Again, this is very similar to how `Record Arguments <http://docs.zope.org/zope2/zdgbook/ObjectPublishing.html?highlight=record#record-arguments>`_ are parsed by ZPublisher, except that you can omit the ``:record`` suffix.


Restricting search to multiple paths
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To restrict search to multiple paths, the original query as a Python dictionary would look like this (with an optional depth and sort_on)::

    query = {'path': {'query': ('/folder', '/folder2'),
                      'depth': 2},
             'sort_on': 'path'}

This dictionary will need to be flattened in dotted notation in order to pass it in a query string. In order to specify multiple paths, simply repeat the query string parameter (the ``requests`` module will do this automatically for you if you pass it a list of values for a query string parameter).

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/search_multiple_paths.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/search_multiple_paths.resp
   :language: http


Data types in queries
^^^^^^^^^^^^^^^^^^^^^

Because HTTP query strings contain no information about data types, any query string parameter value ends up as a string in the Zope request.
This means that for value types that aren't string these data types need to be reconstructed on the server side in plone.restapi.

For most index types and their query values and query options plone.restapi can handle this for you.
If you pass it ``path.query=foo&path.depth=1``, it has the necessary knowledge about the ``ExtendedPathIndex``'s options to turn the string ``1`` for the ``depth`` argument back into an integer before passing the query on to the catalog.

However, certain index types (a ``FieldIndex`` for example) may take arbitrary data types as query values.
In that case, ``plone.restapi`` simply can't know what data type to cast your query value to and you'll need to specify it using ZPublisher type hints:

.. code-block:: http

    GET /plone/@search?numeric_field:int=42 HTTP/1.1
    Accept: application/json


Please refer to the `Documentation on Argument Conversion in ZPublisher <http://docs.zope.org/zope2/zdgbook/ObjectPublishing.html#argument-conversion>`_ for details.

.. _retrieving-additional-metadata:

Retrieving additional metadata
------------------------------

By default, the results are represented as summaries that only contain the most basic information about the items, like their URL and title.
If you need to retrieve additional metadata columns, you can do so by specifying the additional column names in the ``metadata_fields`` parameter:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/search_metadata_fields.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/search_metadata_fields.resp
   :language: http

The metadata from those columns will then be included in the results.
In order to specify multiple columns, simply repeat the query string parameter once for every column name (the ``requests`` module will do this automatically for you if you pass it a list of values for a query string parameter).

In order to retrieve all metadata columns that the catalog knows about, use ``metadata_fields=_all``.

.. note::
        There is a difference between the full set of fields contained in an object and the set of all possible metadata columns that can be specified with ``metadata_fields``.
        In other words, using ``metadata_fields=_all`` will produce objects with a set of fields that is generally smaller than the set of fields produced by ``fullobjects`` (see next section).
        Briefly, the fields in ``metadata_fields=_all`` are a subset of ``fullobjects``.
        A consequence of this is that certain fields can not be specifed with ``metadata_fields``.
        Doing so will result in a TypeError ``"No converter for making <...> JSON compatible."``
        In `ZCatalog <https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html>`_ terms, this reflects the difference between *catalog brains* and objects that have been *woken up*.


Retrieving full objects
-----------------------

If the data provided as metadata is not enough, you can retrieve search results as full serialized objects equivalent to what the resource GET request would produce.

You do so by specifying the ``fullobjects`` parameter:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/search_fullobjects.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/search_fullobjects.resp
   :language: http

.. warning::

    Be aware that this might induce performance issues when retrieving a lot of resources. Normally the search just serializes catalog brains, but with ``fullobjects``, we wake up all the returned objects.


Restrict search results to Plone's search settings
--------------------------------------------------
By default the search endpoint is not excluding any types from its results. To allow the search to follow Plone's search settings schema, pass the ``use_site_search_settings=1`` to the ``@search`` endpoint request. By doing this, the search results will be filtered based on the defined types to be searched and will be sorted according to the default sorting order.
