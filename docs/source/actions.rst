Portal Actions
================

You can get the available actions for a user on a context with the
@actions endpoint. A part of the actions are global. The
content object related actions depend on the type, content and the users
permissions on the object.


Reading the actions
-------------------

.. http:example:: curl httpie python-requests
   :request: _json/actions_get.req

Example 

.. literalinclude:: _json/actions_get.resp
   :language: http
