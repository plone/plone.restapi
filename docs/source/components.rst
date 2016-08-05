Components
==========

How to get pages components (i.e. everything but the main content), like breadcrumbs, navigations, actions, etc.

Breadcrumbs
-----------

Getting the breadcrumbs for the current page:

.. code::

  GET /:portal/:path_to_content/@components/breadcrumbs HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/breadcrumbs.json
   :language: js

Navigation
-------------------------

Getting the top navigation items:

.. code::

  GET /:portal/@components/navigation HTTP/1.1
  Host: localhost:8080
  Accept: application/json

Example:

.. literalinclude:: _json/navigation.json
   :language: js
