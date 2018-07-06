Locking
=======

Locking is a mechanism to prevent users from accidentially overriding each others changes.

When a user edits a content object in Plone, the object is locked until the user hits the save or cancel button.
If a second user tries to edit the object at the same time, she will see a message that this object is locked.


Locking an object
-----------------

To lock an object send a POST request to the ``/@lock`` endpoint that is available on any content object in Plone:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/lock.req

If the lock operation succeeds, the server will respond with status :term:`200 OK` and return various information
about the lock including the lock token. The token is needed in later requests to update the locked object.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/lock.resp
   :language: http


By default, locks are stealable. That means that another user can unlock the object.
If you want to create a non-stealable lock, pass ``"stealable": false`` in the request body.

To create a lock with a non-default timeout, you can pass the the timeout value in seconds in the request body.

The following example creates a non-stealable lock with a timeout of 1h.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/lock_nonstealable_timeout.req


The server responds with status :term:`200 OK` and returns the lock information.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/lock_nonstealable_timeout.resp
   :language: http


Unlocking an object
-------------------

To unlock an object send a POST request to the ``/@unlock`` endpoint.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/unlock.req

The server responds with status :term:`200 OK` and returns the lock information.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/unlock.resp
   :language: http


Refreshing a lock
-----------------

An existing lock can be refreshed by sending a POST request to the ``@refresh-lock`` endpoint.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/refresh_lock.req

The server responds with status :term:`200 OK` and returns the lock information containing the updated creation time.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/refresh_lock.resp
   :language: http


Getting lock information
------------------------

To find out if an object is locked or to get information about the current lock
you can send a GET request to the ``@lock`` endpoint.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/lock_get.req

The server responds with status :term:`200 OK` and returns the information about the lock.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/lock_get.resp
   :language: http


Updating a locked object
------------------------

To update a locked object with a PATCH request, you have to provide the lock
token with the ``Lock-Token`` header.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/lock_update.req
