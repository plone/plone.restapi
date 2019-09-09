Querystring Search
==================

The ``@querystring-search`` endpoint given a p.a.querystring query returns the results.

You can call the ``/@querystring-search`` endpoint with a ``POST`` request and the p.a.querystring query in JSON BODY, along with the others querystring options:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/querystringsearch_post.req

The server will respond with the results:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/querystringsearch_post.resp
   :language: http
