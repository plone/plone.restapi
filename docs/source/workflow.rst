Workflow
========

.. note::
   Currently the workflow support is limited to executing transitions on content.

In Plone, content almost always has a :term:`workflow` attached.
We can get the current state and history of an object by issuing a ``GET`` request using on any context:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workflow_get.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workflow_get.resp
   :language: http


Now, if we want to change the state of the front page to publish, we would proceed by issuing a ``POST`` request to the given URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workflow_post.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workflow_post.resp
   :language: http


We can also also change the state recursively for all contained items, provide a comment and set effective and expiration dates:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workflow_post_with_body.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workflow_post_with_body.resp
   :language: http
