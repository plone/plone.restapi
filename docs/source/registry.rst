Registry
========

Registry records can be addressed by using the fully qualified dotted name of
the registry record to be read/written as the ``:name`` parameter.

Reading or writing registry records requires the ``cmf.ManagePortal`` permission.

Reading registry records
------------------------

Reading a single record:

.. code::

  GET /:portal/@registry/:name HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/registry_get.json
   :language: js

Updating registry records
-------------------------

Updating an existing record:

.. code::

  PATCH /:portal/@registry/ HTTP/1.1
  Host: localhost:8080
  Accept: application/json

  {name: value}

Example:

.. literalinclude:: _json/registry_update.json
   :language: js
