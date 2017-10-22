Interfaces
==========

*Interfaces are objects that specify the external behavior of objects
that "provide" them.* (from `zope.interface documentation`_)

All objects in Plone have one or more interface which they provide and in some cases knowing those interfaces
is interesting to act accordingly. For instance many views are registered to be available just for objects
providing certain interfaces, or navigation and searches are restricted to the contents of objects providing
the *INavigationRoot* interface.

To get the interfaces provided by an object context we need to issue a ``GET`` request:

...  http:example:: curl httpie python-requests
    :request: _json/interfaces.req

The response will include all provided interfaces:

... literalinclude:: _json/interfaces.resp
   :language: http

.. _`zope.interface documentation`: https://docs.zope.org/zope.interface/README.html