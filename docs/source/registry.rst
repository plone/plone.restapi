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
    :request: _json/registry_get.req

Example Response:

.. literalinclude:: _json/registry_get.resp
   :language: http

Updating registry records
-------------------------

Updating an existing record:

..  http:example:: curl httpie python-requests
    :request: _json/registry_update.req

Example Response:

.. literalinclude:: _json/registry_update.resp
   :language: http