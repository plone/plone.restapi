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
