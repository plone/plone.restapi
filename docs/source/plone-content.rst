Plone Content
=============

How to get all standard Plone content representations.
The syntax is given in various tools, click on 'curl', 'http-request' or 'python-requests' to see examples.

.. note::
        For folderish types, collections or search results, the results will
        be **batched** if the size of the resultset exceeds the batch size.
        See :doc:`/batching` for more details on how to work with batched
        results.


Plone Portal Root:
------------------

..  http:example:: curl httpie python-requests
    :request: _json/siteroot.req

.. literalinclude:: _json/siteroot.resp
   :language: http


Plone Folder:
-------------

..  http:example:: curl httpie python-requests
    :request: _json/folder.req

.. literalinclude:: _json/folder.resp
   :language: http


Plone Document:
---------------

..  http:example:: curl httpie python-requests
    :request: _json/document.req

.. literalinclude:: _json/document.resp
   :language: http


News Item:
----------

..  http:example:: curl httpie python-requests
    :request: _json/newsitem.req

.. literalinclude:: _json/newsitem.resp
   :language: http


Event:
------

..  http:example:: curl httpie python-requests
    :request: _json/event.req

.. literalinclude:: _json/event.resp
   :language: http


Image:
------

..  http:example:: curl httpie python-requests
    :request: _json/image.req

.. literalinclude:: _json/image.resp
   :language: http


File:
-----

..  http:example:: curl httpie python-requests
    :request: _json/file.req

.. literalinclude:: _json/file.resp
   :language: http


Link:
-----

..  http:example:: curl httpie python-requests
    :request: _json/link.req

.. literalinclude:: _json/link.resp
   :language: http


Collection:
-----------

..  http:example:: curl httpie python-requests
    :request: _json/collection.req

.. literalinclude:: _json/collection.resp
   :language: http
