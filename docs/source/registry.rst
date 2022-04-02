Registry
========

Registry records can be addressed through the ``@registry`` endpoint on the
Plone site. In order to address a specific record, the fully qualified dotted
name of the registry record has to be passed as a path segment
(e.g. `/plone/@registy/my.record`).

Reading or writing registry records require the ``cmf.ManagePortal``
permission.

Reading registry records
------------------------

Reading a single record:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/registry_get.req

Example Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/registry_get.resp
   :language: http


Listing registry records
------------------------

The registry records listing uses a batched method to access all registry records.
See :doc:`/batching` for more details on how to work with batched results.

The output per record contains the following fields:
name: The record's fully qualified dotted name.
value: The record's value. This is the same as GETting `@registry/name`.


..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/registry_get_list.req

Example Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/registry_get_list.resp
   :language: http


Updating registry records
-------------------------

Updating an existing record:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/registry_update.req

Example Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/registry_update.resp
   :language: http