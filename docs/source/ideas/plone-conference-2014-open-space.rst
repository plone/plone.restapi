==============================================================================
OPEN SPACE - PLONE CONFERENCE 2014
==============================================================================

Design Decisions
----------------

- RESTful API
- Hypermedia / linked-data
- JSON API
- API Calls should use header to set JSON format and versioning.
- Versioning should be included but we will decide later if we want to support
  multiple versions at the same time
- Field names just map over. Do not try to rewrite attributes (e.g. isPrincipiaFoldish -> is_folderish)


Process
-------

- Design & documentation first
- Tests and testing infrastructure second
- Start working on the implementation only if docs and tests are set up.
- Do proof-of-concepts to make sure our basic design will work

Zupo offered to review our process and makes sure we are doing it right (like
plone.api).


Scope
-----

Start with a minimal viable API and go on from there:

1) Just browse as anonymous user (GET ONLY)
2) Authentication
3) Basic CRUD + workflow
4) Expose full Plone API


Existing Standards
------------------

- JSON-LD
- JSON Schema
- Hydra
- Collection+JSON
- ...


Existing Tools
--------------

- APIary: https://app.apiary.io/plonerestapi
- Swagger: http://petstore.swagger.wordnik.com/


Testing
-------

- Sphinx-based?
- Robot-Framework based?


Proof of Concept
----------------

- ZServer GET/POST/PUT/DELETE
- Convert: Dexerity Object -> JSON
- JSON-LD


plone.restapi
-------------

https://github.com/plone/plone.restapi
http://plonerestapi.readthedocs.org/en/latest/



People
------

People willing to review API:

- laurence
- Martin
- Nejc
- Ramon
- Maurits
- Harald friesenegger
- Gil
- davisagli
- martior
- witsch
