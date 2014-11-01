==============================================================================
A JSON-LD / Hydra Web API for Plone
==============================================================================

Introduction
------------

"Linked Data is a way to create a network of standards-based machine interpretable data across different documents and Web sites. It allows an application to start at one piece of Linked Data, and follow embedded links to other pieces of Linked Data that are hosted on different sites across the Web."

http://www.w3.org/TR/json-ld

JSON-LD / Hydra provides a schema and a way to link resources.

Schema => @context / @type
Links => @id / Collection.member


Linked Data / Hypermedia / HATEOAS
----------------------------------

Plone Portal Root (A Hydra Collection)::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/++api++v1/",
    "@type": "Collection",
    "member": [
      {
        "@id": "http://localhost:8080/Plone/++api++v1/front-page",
        "title": "Welcome to Plone",
        "description": "Congratulations! You have successfully installed Plone."
      },
      {
        "@id": "http://localhost:8080/Plone/++api++v1/news",
        "title": "News",
        "description": "Plone Site News"
      },
      {
        "@id": "http://localhost:8080/Plone/++api++v1/events",
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

=> You can follow links (@id property) to other resources. Those resources can
be collections or resources.


Plone Document (A Hydra Resource)::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/++api++v1/doc1",
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


Entry Point
-----------

Every resource contains a link to the entrypoint of the API

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "entrypoint": "http://localhost:8080/Plone/++api++v1",
    ...
  }


API Documentation
-----------------

{
  "@context": "http://www.w3.org/ns/hydra/context.jsonld",
  "@id": "http://localhost:8080/Plone/++api++v1/doc/",
  "@type": "ApiDocumentation",
  "title": "Plone RESTful API Documentation",
  "description": "A short description of the API",
}
