Add-ons
========

Addon product records can be addressed through the ``@addons`` endpoint on the
Plone site. In order to address a specific record, the profile id has to be
passed as a path segment (e.g. `/plone/@addons/plone.session`).

Reading or writing addons metadata require the ``cmf.ManagePortal``
permission.

Reading add-ons records
-----------------------

Reading a single record:

..  http:example:: curl httpie python-requests
    :request: _json/addons_get.req

Example Response:

.. literalinclude:: _json/addons_get.resp
   :language: http


Listing add-ons records
-----------------------

The registry records listing uses a batched method to access all addons.
See :doc:`/batching` for more details on how to work with batched results.


..  http:example:: curl httpie python-requests
    :request: _json/addons_get_list.req

Example Response:

.. literalinclude:: _json/addons_get_list.resp
   :language: http
