.. image:: https://secure.travis-ci.org/plone/plone.restapi.png?branch=master
  :target: http://travis-ci.org/plone/plone.restapi

.. image:: https://coveralls.io/repos/plone/plone.restapi/badge.png?branch=master
  :target: https://coveralls.io/r/plone/plone.restapi

.. image:: https://readthedocs.org/projects/pip/badge/
  :target: https://plonerestapi.readthedocs.org

.. image:: https://landscape.io/github/plone/plone.restapi/master/landscape.svg?style=plastic
  :target: https://landscape.io/github/plone/plone.restapi/master
  :alt: Code Health

.. image:: https://badge.waffle.io/plone/plone.restapi.png?label=ready&title=Ready
 :target: https://waffle.io/plone/plone.restapi
 :alt: 'Stories in Ready'


Introduction
============

plone.restapi is a RESTful hypermedia API for Plone.


RESTful Hypermedia API
----------------------

REST stands for `Representational State Transfer <http://en.wikipedia.org/wiki/Representational_state_transfer>`_. It is a software architectural principle to create loosely coupled web APIs.

Most web APIs have a tight coupling between client and server. This makes them brittle and hard to change over time. It requires them not only to fully document every small detail of the API, but also write a client implementation that follows that specification 100% and breaks as soon as you change any detail.

A hypermedia API just provides an entry point to the API that contains hyperlinks the clients can follow. Just like a human user of a regular website, that knows the initial URL of a website and then follows hyperlinks to navigate through the site. This has the advantage that the client just needs to understand how to detect and follow links. The URL and other details of the API can change without breaking the client.


Documentation
=============

http://plonerestapi.readthedocs.org


Roadmap
=======

https://github.com/plone/plone.restapi/milestones


Live Demo
=========

Heroku live demo:: http://stormy-headland-44390.herokuapp.com/Plone/

.. note:: You will need some kind of API browser application to explore the API. We recommend to use `Postman <http://www.getpostman.com/>`_.


Design Decisions
================

* A truly RESTful API (Hypermedia / HATEOAS / Linked-data)
* JSON is the main target formt, support other formats (HTML, XML) later
* Use HTTP headers (to set format and versioning, also provide URL-based option to make it easier for people to try it out)
* No versioning, version in the HTTP header can be added later
* Field names just map over (we will not try to clean up attributes or enforce naming standards like pep8 (e.g. isPrincipiaFoldish -> is_folderish)


Software Quality
================

* 100% Test Coverage
* 100% PEP8 compliant


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
