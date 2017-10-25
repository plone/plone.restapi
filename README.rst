.. image:: https://secure.travis-ci.org/plone/plone.restapi.png?branch=master
  :target: http://travis-ci.org/plone/plone.restapi

.. image:: https://coveralls.io/repos/github/plone/plone.restapi/badge.svg?branch=master
  :target: https://coveralls.io/github/plone/plone.restapi?branch=master

.. image:: https://landscape.io/github/plone/plone.restapi/master/landscape.svg?style=flat
   :target: https://landscape.io/github/plone/plone.restapi/master
   :alt: Code Health

.. image:: https://readthedocs.org/projects/pip/badge/
  :target: https://plonerestapi.readthedocs.org

.. image:: https://img.shields.io/pypi/v/plone.restapi.svg
  :target: https://pypi.python.org/pypi/plone.restapi


Introduction
============

plone.restapi is a RESTful hypermedia API for Plone.


RESTful Hypermedia API
----------------------

REST stands for `Representational State Transfer <http://en.wikipedia.org/wiki/Representational_state_transfer>`_. It is a software architectural principle to create loosely coupled web APIs.

Most web APIs have a tight coupling between client and server. This makes them brittle and hard to change over time. It requires them not only to fully document every small detail of the API, but also to write a client implementation that follows that specification 100% correctly and breaks as soon as you change any detail.

A hypermedia API just provides an entry point to the API that contains hyperlinks the clients can follow, just as a human user of a regular website knows the initial URL of the site and then follows hyperlinks to navigate through the site. This has the advantage that the client needs to understand only how to detect and follow links. The URL and other details of the API can change without breaking the client.


Documentation
=============

http://plonerestapi.readthedocs.org


Roadmap
=======

https://github.com/plone/plone.restapi/milestones


Live Demo
=========

A live demo of Plone 5 with the latest plone.restapi release is available at:

http://plonedemo.kitconcept.com

Example GET request on the portal root::

  $ curl -i http://plonedemo.kitconcept.com -H "Accept: application/json"

Example POST request to create a new document::

  $ curl -i -X POST http://plonedemo.kitconcept.com -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"@type": "Document", "title": "My Document"}' --user admin:admin

.. note:: You will need some kind of API browser application to explore the API. We recommend using `Postman <http://www.getpostman.com/>`_.


Design Decisions
================

* A truly RESTful API (Hypermedia / HATEOAS / Linked-data)
* JSON is the main target format; support for other formats (HTML, XML) will come later
* Use HTTP headers (to set format and versioning, also provide URL-based option to make it easier for people to try it out)
* No versioning; versioning in the HTTP header can be added later
* Field names just map over (we will not try to clean up attributes or enforce naming standards like pep8 (e.g. isPrincipiaFoldish -> is_folderish)


Software Quality
================

* 100% test coverage
* 100% PEP8 compliant
* Documentation-first approach for enhancements


Further Reading
===============

* `REST in Practice: Hypermedia and Systems Architecture (Webber, Parastatidis, Robinson) <http://www.amazon.com/gp/product/0596805829>`_


Standards
=========

- `JSON-LD <http://www.w3.org/TR/json-ld/>`_
- `JSON Schema <http://json-schema.org/>`_
- `Schema.org <http://schema.org/>`_
- `Hydra <http://www.w3.org/ns/hydra/spec/latest/core/>`_
- `Collection+JSON <http://amundsen.com/media-types/collection/>`_
- `Siren <https://github.com/kevinswiber/siren>`_


License
=======

The project is licensed under the GPLv2.
