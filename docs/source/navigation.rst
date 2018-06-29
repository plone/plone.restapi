.. _navigation:

Navigation
==========

Top-Level Navigation
--------------------

Getting the top navigation items:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navigation.req

Example response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/navigation.resp
   :language: http


Navigation Tree
---------------

Getting the navigation item tree providing a `expand.navigation.depth` parameter:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/navigation_tree.req

Example response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/navigation_tree.resp
   :language: http
