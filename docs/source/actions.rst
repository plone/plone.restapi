Portal Actions
==============

Plone has the concept of configurable action (called "portal_actions"). 
They are sorted by categories. They define an id, a title, the required
permission and a condition that will be checked to decide if the action 
will be available for a user.

Actions are used to create variable actions in the UI. Examples are the 
object tabs (view, edit, folder contents, sharing) or the user
actions (login, logout, preferences). The action providers in Plone used
in this endpoint are ``portal_actions`` and ``portal_types``.

You can get the available actions for a user on a specific context by
calling the @actions endpoint. This also works for not authenticated users.  
If you want to limit the categories, you can pass one or more parameters
``categories:list``, i.e. ``@action?categories:list=object&categories:list=user``.


Reading the actions
-------------------

.. http:example:: curl httpie python-requests
   :request: _json/actions_get.req

Example 

.. literalinclude:: _json/actions_get.resp
   :language: http
