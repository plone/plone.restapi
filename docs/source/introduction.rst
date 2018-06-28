Introduction
============

.. sidebar:: API Browser Quick Guide
    :subtitle: **It can make your life easier** if you use some kind of **API browser application** to **explore the API** when diving into this documentation.

    * We recommend to use the free `Postman <http://www.getpostman.com/>`_ browser plugin. 
    * For easy onboarding take a look at **our** :ref:`exploring-api-postman-onboarding` **Quick-Guide**.

A hypermedia API provides an entry point to the API, which contains hyperlinks the clients can follow.
Just like a human user of a regular website, who knows the initial URL of a website and then follows hyperlinks to navigate through the site.
This has the advantage that the client only needs to understand how to detect and follow links.
The URLs (apart from the inital entry point) and other details of the API can change without breaking the client.

The entry point to the Plone RESTful API is the portal root.
The client can ask for a :term:`REST` API response by setting the ``'Accept'`` HTTP header to ``'application/json'``:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/siteroot.req


This uses so-called 'content negotiation'

  .. toctree::
   :maxdepth: 1

    More on Content Negotiation <content-negotiation>

The server will then respond with the portal root in the JSON format:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/siteroot.resp
   :language: http

``@id`` is a unique identifier for resources (IRIs).
The ``@id`` property can be used to navigate through the web API by following the links.

``@type`` sets the data type of a node or typed value

``items`` is a list that contains all objects within that resource.

A client application can "follow" the links (by calling the @id property) to other resources.
This allows to build a losely coupled client that does not break if some of the URLs change, only the entry point of the entire API (in our case the portal root) needs to be known in advance.

Another example, this time showing a request and response for a document.
Click on the buttons below to show the different syntaxes for the request.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/document.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/document.resp
   :language: http

And so on, see

  .. toctree::
   :maxdepth: 1

     Representation of all standard Plone contenttypes<plone-content>