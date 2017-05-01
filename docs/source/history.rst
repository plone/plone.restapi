History
=======

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

- action: the workflow transition id, 'Edited' for versioning, or 'Create' for initial state.
- actor: the user who performed the action. This contains a subobject with the details.
- comments: a changenote
- @id: link to the content endpoint of this specific version.
- may_revert: true if the user has permission to revert.
- time: when this action occured in ISO format.
- transition_title: the workflow transition's title, 'Edited' for versioning, or 'Create' for initial state.
- type: 'workflow' for workflow changes, 'versioning' for editing, or null for content creation.
- version: identifier for this specific version of the resource.


GET historical versions
-----------------------

Older versions of resources can be retrieved by append the `version` to the @history endpoint url.

..  http:example:: curl httpie python-requests
    :request: _json/history_get_versioned.req


PATCH revert historical versions
--------------------------------

Reverting to older versions of a resource can be done by issueing a PATCH request with a version.

..  http:example:: curl httpie python-requests
    :request: _json/history_revert.req

.. literalinclude:: _json/history_revert.resp
   :language: http
