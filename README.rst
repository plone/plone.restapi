.. image:: https://secure.travis-ci.org/plone/plone.restapi.png?branch=master
  :target: http://travis-ci.org/plone/plone.restapi

.. image:: https://coveralls.io/repos/github/plone/plone.restapi/badge.svg?branch=master
  :target: https://coveralls.io/github/plone/plone.restapi?branch=master

.. image:: https://landscape.io/github/plone/plone.restapi/master/landscape.svg?style=flat
   :target: https://landscape.io/github/plone/plone.restapi/master
   :alt: Code Health

.. image:: https://readthedocs.org/projects/pip/badge
  :target: https://plonerestapi.readthedocs.org

.. image:: https://img.shields.io/pypi/v/plone.restapi.svg
  :target: https://pypi.python.org/pypi/plone.restapi


Introduction
============

plone.restapi is a RESTful hypermedia API for Plone.


Documentation
=============

http://plonerestapi.readthedocs.org


Getting started
===============

A live demo of Plone 5 with the latest plone.restapi release is available at:

http://plonedemo.kitconcept.com

Example GET request on the portal root::

  $ curl -i https://plonedemo.kitconcept.com -H "Accept: application/json"

Example POST request to create a new document::

  $ curl -i -X POST https://plonedemo.kitconcept.com -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"@type": "Document", "title": "My Document"}' --user admin:admin

.. note:: You will need some kind of API browser application to explore the API. We recommend using `Postman <http://www.getpostman.com/>`_.


Installation
============

Install plone.restapi by adding it to your buildout::

    [buildout]

    ...

    eggs =
        plone.restapi


and then running ``bin/buildout``


Contribute
==========

- Issue Tracker: https://github.com/plone/plone.restapi/issues
- Source Code: https://github.com/plone/plone.restapi
- Documentation: https://plonerestapi.readthedocs.io/en/latest


Examples
========

plone.restapi is used in production since the first alpha release.
It can be seen in action at the following sites:

- Zeelandia GmbH & Co. KG: https://www.zeelandia.de (by kitconcept GmbH)
- VHS-Ehrenamtsportal: https://vhs-ehrenamtsportal.de (by kitconcept GmbH)
- German Physical Society: https://www.dpg-physik.de (by kitconcept GmbH)
- Universitat Politècnica de Catalunya: https://www.upc.edu (by kitconcept GmbH)

Support
=======

If you are having issues, please let us know via the issue tracker.

If you required professional support, here is a list of Plone solution providers that contributed significantly to plone.restapi in the past:

- kitconcept GmbH (Germany) https://kitconcept.com
- 4teamwork (Switzerland) https://www.4teamwork.ch
- CodeSyntax (Spain) https://www.codesyntax.com/en


License
=======

The project is licensed under the GPLv2.
