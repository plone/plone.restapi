Portlets
========

The @portlets endpoint is context specific.

Called on the portal root it will list all available portlet managers.

(TODO - it works for all content not just the site. Can we have local portlet managers in plone?)

(TODO: separate manager on type: context, dashboard, user/group, contenttype, etc.)

If called on a content object with a portlet manager id, it will return the portlets for this context and manager.

Listing available portlet managers
----------------------------------

List all available portlet managers by sending a GET request to the @portlets endpoint on the portal root:

..  http:example:: curl httpie python-requests
    :request: _json/portlets_get.req

The server responds with a `Status 200` and list all available managers:

.. literalinclude:: _json/portlets_get.resp
   :language: http



Retrieve portlets for a portlet manager
---------------------------------------

Retrieve the portlets of a specific portlet manager by calling the '@portlets' endpoint with the id of the manager:


..  http:example:: curl httpie python-requests
    :request: _json/portlets_get_left_column.req

The server responds with:


.. literalinclude:: _json/portlets_get_left_column.resp
   :language: http


Or:


..  http:example:: curl httpie python-requests
    :request: _json/portlets_get_right_column.req

The server responds with:


.. literalinclude:: _json/portlets_get_right_column.resp
   :language: http


Retrieving portlets on a context
--------------------------------

Retrieve the portlets of a specific context / portlet manager by calling the '@portlets' endpoint on the context with the id of the manager:


..  http:example:: curl httpie python-requests
    :request: _json/portlets_get_left_column_doc.req

The server responds with:


.. literalinclude:: _json/portlets_get_left_column_doc.resp
   :language: http



Adding portlets
---------------

TODO


Updating a portlet with PATCH
-----------------------------

TODO


Removing a portlet with DELETE
------------------------------

TODO


Reordering portlets
-------------------

TODO
