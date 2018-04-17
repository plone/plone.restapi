.. _navigation:

Navigation
==========

Top-Level Navigation
--------------------

Getting the top navigation items:

..  http:example:: curl httpie python-requests
    :request: _json/navigation.req

Example response:

.. literalinclude:: _json/navigation.resp
   :language: http


Navigation Tree
---------------

Getting the navigation item tree providing a `expand.navigation.depth` parameter:

..  http:example:: curl httpie python-requests
    :request: _json/navigation_tree.req

Example response:

.. literalinclude:: _json/navigation_tree.resp
   :language: http
