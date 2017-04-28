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

This following fields are returned:
  action: the workflow transition id, or 'Edited' for versioning.
  actor: the user who performed the action. This contains a subobject with the details.
  comments: a changenote
  content_url: link to the content endpoint of this specific version.
  may_revert: true if the user has permission to revert.
  time: when this action occured in ISO format.
  transition_title: the workflow transition's title, for 'Edited' for versioning.
  type: 'workflow' for workflow changes, 'versioning' for editing, or null for content creation.
  version_id: identifier for this specific version of the resource.


PATCH revert historical versions
--------------------------------

Reverting to older versions of a resource can be done by issueing a PATCH request with a version_id.

..  http:example:: curl httpie python-requests
    :request: _json/history_revert.req

.. literalinclude:: _json/history_revert.resp
   :language: http
