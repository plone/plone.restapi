Introduction
============

A hypermedia API just provides an entry point to the API that contains hyperlinks the clients can follow. Just like a human user of a regular website, that knows the initial URL of a website and then follows hyperlinks to navigate through the site. This has the advantage, that the client just needs to understand how to detect and follow links. The URL and other details of the API can change without breaking the client.

The entry point to the Plone RESTful API is the portal root. The client can ask for a REST API response by setting the 'Accept' HTTP header to 'application/json'::

  GET /
  Accept: application/json

The server will then respond with the portal root in the JSON format:

.. literalinclude:: _json/siteroot.json
   :language: json-ld

`@id` is a unique identifier for resources (IRIs). The @id property can be used to navigate through the web API by following the links.

`@type` sets the data type of a node or typed value

`member` is a list containing all objects within that resource.

=> A web client can follow the links (@id property) to other resources.


Plone Content
-------------

Plone Portal Root:

.. literalinclude:: _json/siteroot.json
   :language: json-ld

Plone Folder:

.. literalinclude:: _json/folder.json
   :language: jsonld

Plone Document:

.. literalinclude:: _json/document.json
   :language: jsonld

News Item:

.. literalinclude:: _json/newsitem.json
   :language: json-ld

Event:

.. literalinclude:: _json/event.json
   :language: json-ld

Image:

.. literalinclude:: _json/image.json
   :language: json-ld

File:

.. literalinclude:: _json/file.json
   :language: json-ld

Link:

.. literalinclude:: _json/link.json
   :language: json-ld

Collection:

.. literalinclude:: _json/collection.json
   :language: json-ld
