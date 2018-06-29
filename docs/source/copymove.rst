Copy / Move
===========

Copying an object
-----------------

To copy a content object send a POST request to the ``/@copy`` endpoint at the
destinations url with the source object specified in the request body. The source
object can be specified either by url, path, UID or intid.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/copy.req

If the copy operation succeeds, the server will respond with status 200 (OK) and return
the new and old url of the copied object.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/copy.resp
   :language: http


Moving an object
----------------

To move a content object send a POST request to the ``/@move`` endpoint at the
destinations url with the source object specified in the request body. The source
object can be specified either by url, path, UID or intid.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/move.req

If the move operation succeeds, the server will respond with status 200 (OK) and return
the new and old url of the moved object.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/move.resp
   :language: http


Copying/moving multiple objects
-------------------------------

Multiple objects can be moved/copied by giving a list of sources.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/copy_multiple.req

If the operation succeeds, the server will respond with status 200 (OK) and return
the new and old urls for each copied/moved object.


.. literalinclude:: ../../src/plone/restapi/tests/http-examples/copy_multiple.resp
   :language: http
