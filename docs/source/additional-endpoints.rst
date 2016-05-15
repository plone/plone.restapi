Additional Endpoints (MOCKS ONLY)
=================================

These are mocked endpoints for use during the Barcelona 2016 Sprint.

.. meta::
   :robots: noindex, nofollow

.. warning::
   These endpoints simply deliver mocked content (canned responses). They are
   not intended for actual use, but instead serve as a skeleton to flesh out
   different aspects of the API during the Barcelona 2016 sprint.


Registry
========

Registry records can be addressed by using the fully qualified dotted name of
the registry record to be read/written as the ``:name`` parameter.

Reading registry records
------------------------

Reading a single record:

.. code::

  GET /:portal/registry_/:name HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/registry_get.json
   :language: js

Updating registry records
-------------------------

Updating an existing record:

.. code::

  PUT /:portal/registry_/ HTTP/1.1
  Host: localhost:8080
  Accept: application/json

  {name: value}

Example:

.. literalinclude:: _json/registry_update.json
   :language: js


Theme
========

Requesting for overridden resources
-----------------------------------

.. code::

  GET /:portal/theme_ HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/theme.json
   :language: js


Components
==========

Get the required component(s)
------------------------------

.. code::

 GET /:portal/components_/:[id,] HTTP/1.1
 Host: localhost:8080
 Accept: application/json

Example:

.. literalinclude:: _json/components.json
  :language: js


Actions
==========

Get the available actions for the given context
-----------------------------------------------

.. code::

 GET /:path/actions_ HTTP/1.1
 Host: localhost:8080
 Accept: application/json

Example:

.. literalinclude:: _json/actions.json
  :language: js
