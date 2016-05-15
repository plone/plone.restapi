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

Reading registry records
------------------------

.. code::

  GET /:site/registry_/:record_name HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/registry.json
   :language: js

Theme
========

Requesting for overridden resources
-----------------------------------

.. code::

  GET /:site/theme_ HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/theme.json
  :language: js
