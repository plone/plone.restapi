Batching
========

Representations of collection-like resources are batched / paginated if the
size of the resulset exceeds the batching size:

.. code-block:: json

    {
      "@id": "http://.../folder/search",
      "batching": {
        "@id": "http://.../folder/search?b_size=10&b_start=20",
        "first": "http://.../plone/folder/search?b_size=10&b_start=0",
        "last": "http://.../plone/folder/search?b_size=10&b_start=170",
        "prev": "http://.../plone/folder/search?b_size=10&b_start=10",
        "next": "http://.../plone/folder/search?b_size=10&b_start=30"
      },
      "items": [
        "..."
      ],
      "items_total": 175,
    }

If the entire resulset fits into a single batch page (as determined by
``b_size``), the top-level ``batching`` links will be omitted.


Top-level attributes
--------------------

================ ===========================================================
Attribute        Description
================ ===========================================================
``@id``          Canonical base URL for the resource, without any
                 batching parameters
``items``        Current batch of items / members of the collection-like
                 resource
``items_total``  Total number of items
``batching``     Batching related navigation links (see below)
================ ===========================================================


Batching links
--------------

If, and only if, the resultset has been batched over several pages, the
response body will contain a top-level attribute ``batching`` that contains
batching links. These links that can be used to navigate batches in a
Hypermedia fashion:

================ ===========================================================
Attribute        Description
================ ===========================================================
``@id``          Link to the current batch page
``first``        Link to the first batch page
``prev``         Link to the previous batch page (*if applicable*)
``next``         Link to the next batch page (*if applicable*)
``last``         Link to the last batch page
================ ===========================================================



Parameters
----------

Batching can be controlled with two query string parameters. In order to
address a specific batch page, the ``b_start`` parameter can be used to
request a specific batch page, containing ``b_size`` items starting from
``b_start``.

================ ===========================================================
Parameter        Description
================ ===========================================================
``b_size``       Batch size (default is 25)
``b_start``      First item of the batch
================ ===========================================================


Full example of a batched request and response:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/batching.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/batching.resp
   :language: http

