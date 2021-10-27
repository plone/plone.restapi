Link integrity
==============

The ``@linkintegrity`` endpoint return a list of possible reference breaches for a list of contents.

You can call the ``/linkintegrity`` endpoint on site root with a ``POST`` request and a list of uids in JSON BODY:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/linkintegrity_post.req

The server will respond with the results:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/linkintegrity_post.resp
   :language: http

The endpoint accepts only a parameter:

  - ``uids``

