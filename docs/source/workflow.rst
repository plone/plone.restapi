Workflow
========

.. note::
   Currently the workflow support is limited to executing transitions on content.

In Plone, content almost always has a :term:`workflow` attached.
We can get the current state and history of an object by issuing a ``GET`` request using on any context:

.. literalinclude:: _json/workflow_get.json
   :language: js

Now, if we want to change the state of the front page to publish, we would proceed by issuing a ``POST`` request to the given URL:

.. literalinclude:: _json/workflow_post.json
   :language: js
