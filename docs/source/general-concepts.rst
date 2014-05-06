.. include:: /alert-noindex.rst

################
General concepts
################


Prefix and versioning
=====================

This API uses a prefix to disambiguate calls to the API from the normal requests. While this is not mandatory for REST APIs, there are two technical constraints that force us to do so:

#. It is necessary to differentiate the request as an API one (think of a dynamic layer)
#. It is necessary to properly support ``PUT``, ``DELETE`` and all the other HTTP verbs without falling into the WebDAV codepath.

The prefix also contains information about the version of the API, a progressive number (like a package version number, but not tigthly related to it), that refers to a specific, published revision of its specifications.

This is extremely important because it allows incremental change and evolution of the API without the need to break compatibility with clients currently using it. A new version of the API could therefore be completely rewritten (in theory) while maintaining compatibility with old clients by simply not dropping the old URLs.

At a practical level, the API URLs always start with::

  /++api++<version>/

For example::

  /++api++1/news/

Should we revise this API with backard-incompatible changes, the new API would have URLs that start with::

  /++api++2/

While the system will continue to reply to the calls made to ``/++api++1/``. Therefore, new clients will use the new URLs, and od clients will not be aware of the change.

.. note::
   This is not entirely true, we plan to provide a way for clients to discover whether the API they are using is the latest, via special calls.


Dialects
========

This API aims to provide a REST API, which means that the hypermedia format used to represent resources can be negotiated between server and client.

To put the above phrasing in a more comprehensible way, we plan to use the ``Accept`` header and let the client decide which format he wants to speak.

If the client wants to speak plain JSON with the API, its requests will contain the following HTTP header::

  Accept: application/json

And the response will have the following HTTP header::

  Content-Type: application/json

For now, this API will only speak "plain JSON", which however is not a hypermedia protocol (and sadly, hypermedia is the foundation of REST).

Therefore when we say "plain JSON" we mean a particular kind of JSON (that is delineated further in this document).

In the future we would like to support JSON-LD_ (which is a hypermedia-capable dialect of JSON), and if the need arises to support other hypermedia formats we have a mechanism to do so.

.. _`JSON-LD`: http://www.w3.org/TR/json-ld/
