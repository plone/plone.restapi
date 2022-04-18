==============================================================================
A JSON-LD / Hydra Web API for Plone
==============================================================================

Introduction
------------

"Linked Data is a way to create a network of standards-based machine interpretable data across different documents and Web sites. It allows an application to start at one piece of Linked Data, and follow embedded links to other pieces of Linked Data that are hosted on different sites across the Web." -- http://www.w3.org/TR/json-ld

"Hydra is a lightweight vocabulary to create hypermedia-driven Web APIs. By specifying a number of concepts commonly used in Web APIs it enables the creation of generic API clients." -- http://www.w3.org/ns/hydra/spec/latest/core/

JSON-LD / Hydra provides a schema and a way to link resources.

Schema => @context / @type
Links => @id (member property in a Hydra Collection)


Linked Data / Hypermedia / HATEOAS
----------------------------------

Plone Portal Root (A Hydra Collection)::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/"
    "@type": "Collection",
    "member": [
      {
        "@id": "http://localhost:8080/Plone/front-page",
        "title": "Welcome to Plone",
        "description": "Congratulations! You have successfully installed Plone."
      },
      {
        "@id": "http://localhost:8080/Plone/news",
        "title": "News",
        "description": "Plone Site News"
      },
      {
        "@id": "http://localhost:8080/Plone/events",
        "title": "Events",
        "description": "Plone Site Events"
      }
    ]
  }

- @context: Defines what kind of resource this is and the meaning of the
  terms used within this resource.
- @id: Unique identifier for resources (IRIs). The @id property can be used to
  navigate through the web API by following the links.
- @type: Set the data type of a node or typed value
- member: A member (item/object/child) of the collection

=> A web client can follow the links (@id property) to other resources.


Plone Document (A Hydra Resource)::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/doc1",
    "@type": "Resource",
    "title": "Welcome to Plone",
    "description": "Congratulations! You have successfully installed Plone."
    "contributors": [ ],
    "creators": ["admin"],
    "effective": "1969-12-31T00:00:00+02:00",
    "exclude_from_nav": "False",
    "expires": "2499-12-31T00:00:00+02:00",
    "icon": "++resource++plone.dexterity.item.gif",
    "isPrincipiaFolderish": "false",
    "language": "en",
    "meta_type": "Dexterity Item",
    "relatedItems": [ ],
    "rights": "",
    "text": "<p>Lorem Ipsum</p>",
  }

Implementation
--------------

Plone Document:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/document.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/document.resp
   :language: http

Plone Folder:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/folder.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/folder.resp
   :language: http

Plone Portal Root:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/siteroot.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/siteroot.resp
   :language: http

Collection:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/collection.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/collection.resp
   :language: http

Plone Image:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/image.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/image.resp
   :language: http

File:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/file.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/file.resp
   :language: http

Link:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/link.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/link.resp
   :language: http

News Item:

..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/newsitem.req

.. literalinclude:: ../../../src/plone/restapi/tests/http-examples/newsitem.resp
   :language: http
