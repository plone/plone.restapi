Content history
===============

The history and versioning information is exposed using the @history endpoint.
It lists the historical versions of the content.

See :ref:`content_get_version` for documentation on reading older versions of a resource.


GET Resource history
--------------------

Listing versions and history of a resource:

..  http:example:: curl httpie python-requests
    :request: _json/history_get.req

.. literalinclude:: _json/history_get.resp
   :language: http


PATCH revert historical versions
--------------------------------

Reverting to older versions of a resource can be done by issueing a PATCH request with a version_id.

..  http:example:: curl httpie python-requests
    :request: _json/history_revert.req

.. literalinclude:: _json/history_revert.resp
   :language: http
