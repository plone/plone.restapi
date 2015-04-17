Introduction
============

.. image:: https://secure.travis-ci.org/plone/plone.restapi.png?branch=master
    :target: http://travis-ci.org/plone/plone.restapi

.. image:: https://coveralls.io/repos/plone/plone.restapi/badge.png?branch=master
    :target: https://coveralls.io/r/plone/plone.restapi

.. image:: https://readthedocs.org/projects/pip/badge/
    :target: https://plonerestapi.readthedocs.org

plone.restapi is a RESTful hypermedia API for Plone.


RESTful Hypermedia API
----------------------

REST stands for `Representational State Transfer`_. It is a software architectural principle to create loosely coupled web APIs.

Most web APIs have a tight coupling between client and server. This makes them brittle and hard to change over time. It requires them not only to fully document every small detail of the API, but also write a client implementation that follows that specification 100% and breaks as soon as you change any detail.

A hypermedia API just provides and entry point to the API that contains  hyperlinks the clients can follow. Just like a human user of a regular website, that knows the initial URL of a website and then follows hyperlinks to navigate through the site. This has the advantage, that the client just needs to understand how to detect and follow links. The URL and other details of the API can change without breaking the client.


Documentation
=============

http://plonerestapi.readthedocs.org


Roadmap
=======

https://github.com/plone/plone.restapi/milestones


Live Demo
=========

Heroku live demo:: http://arcane-sierra-8467.herokuapp.com/Plone/@@json

.. note:: The demo works best with a browser plugin that makes json links clickable in the browser (e.g. https://addons.mozilla.org/de/firefox/addon/jsonview/).


Design Decisions
================

* A truly RESTful API (Hypermedia / HATEOAS / Linked-data)
* JSON is the main target formt, support other formats (HTML, XML) later
* Use HTTP headers (to set format and versioning, also provide URL-based option to make it easier for people to try it out)
* Versioning should be included (we will decide later, if we actually want to support multiple versions at the same time)
* Field names just map over (we will not try to clean up attributes or enforce naming standards like pep8 (e.g. isPrincipiaFoldish -> is_folderish)
* Dexterity only. We will not put effort into supporting Archetypes.

Software Quality
================

* 100% Test Coverage
* 100% PEP8 compliant

.. _`Representational State Transfer`: http://en.wikipedia.org/wiki/Representational_state_transfer
