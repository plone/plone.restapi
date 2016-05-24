Batching
========

Representations of collection-like resources are batched / paginated:

.. code:: json

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

The top-level attribute ``batching`` contains a dictionary with links that
can be used to navigate batches in a Hypermedia fashion:

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


Full example of a batched response:

.. literalinclude:: _json/batching.json
   :language: js
