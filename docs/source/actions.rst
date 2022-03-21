Portal Actions
==============

Plone has the concept of configurable actions (called "portal_actions").
Each actions defines an id, a title, the required
permissions and a condition that will be checked to decide if the action
will be available for a user.
Actions are sorted by categories.

Actions can be used to build UI elements that adapt to the available actions.
An example is the Plone toolbar where the "object_tabs" (view, edit, folder contents, sharing)
and the "user_actions" (login, logout, preferences) are used to display the user only the actions that are allowed for the currently logged in user.

The available actions for the currently logged in user can be retrieved
by calling the @actions endpoint on a specific context.
This also works for not authenticated users.

Listing available actions
-------------------------

To list the available actions, send a GET request to the '@actions' endpoint on a specific content object:

.. http:example:: curl httpie python-requests
   :request: ../../src/plone/restapi/tests/http-examples/actions_get.req

The server will respond with a `200 OK` status code.
The JSON response contains the available actions categories (object, object_buttons, user) on the top level.
Each category contains a list of the available actions in that category:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/actions_get.resp
   :language: http

If you want to limit the categories that are retured, pass one or more parameters
``categories:list``, i.e. ``@action?categories:list=object&categories:list=user``.
