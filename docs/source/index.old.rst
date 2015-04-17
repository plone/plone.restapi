Design Decisions
----------------

Preliminary. Those are currently more goals than final design decisions.

- RESTful API
- Hypermedia / HATEOAS / Linked-data
- Use JSON as main format
- Use HTTP headers (to set format and versioning, also provide URL-based option to make it easier for people to try it out)
- Versioning should be included (we will decide later, if we actually want to support multiple versions at the same time)
- Field names just map over (we will not try to clean up attributes or enforce naming standards like pep8 (e.g. isPrincipiaFoldish -> is_folderish)
- Dexterity only. We will not put effort into supporting Archetypes.


Process
-------

We plan to follow the very successful "design & documentation first" approach of plone.api.

1) Design, discussion, and documentation first
2) Tests and testing infrastructure
3) Proof-of-concept implementations to verify that our basic design will work
4) Implementation

Nejc Zupan offered to review our process and provide advice, if necessary.


Scope
-----

Start with a minimal viable API and go on from there (while iterating over the 'Process' steps):

1) Browse as anonymous user (GET ONLY), most basic Plone functionality
2) Search and other basic Plone functionalities, that do not require authentication
3) Authentication
4) Basic CRUD + Workflow
5) Expose full Plone API


Existing Standards
------------------

Standards that we might take into consideration:

- JSON-LD: http://www.w3.org/TR/json-ld/
- JSON Schema: http://json-schema.org/
- Schema.org: http://schema.org/
- Hydra: http://www.w3.org/ns/hydra/spec/latest/core/
- Collection+JSON: http://amundsen.com/media-types/collection/
- Siren: https://github.com/kevinswiber/siren


Tools
-----

- APIary: https://app.apiary.io/plonerestapi
- Swagger: http://petstore.swagger.wordnik.com/


Testing
-------

- Sphinx-based?
- Robot-Framework based?


Proof of Concept Implementations
--------------------------------

- ZServer (Support for GET/POST/PUT/DELETE):
  https://github.com/tisto/plone.app.angularjs/commit/828440770c22991c38d146bfcf0e1c67559f60d9
- Transformation (Dexerity Object + Behavior -> JSON):
  https://github.com/tisto/plone.app.angularjs/blob/master/src/plone/app/angularjs/utils.py#L9


References
==========

The design of the API has been influenced by the following resources, books, and projects:

REST in Practice: Hypermedia and Systems Architecture

    by Jim Webber, Savas Parastatidis, Ian S Robinson

RESTful Web APIs

   by Leonard Richardson, Mike Amundsen, Sam Ruby

   O'Reilly Media, 2013

   ISBN 978-1-4493-5806-8

   http://shop.oreilly.com/product/0636920028468.do

REST cookbook
   By Joshua Thyssen and others

   http://restcookbook.com

Python-EVE
   A generic RESTful app framework

   by Nicola Iarocci

   http://python-eve.org/
