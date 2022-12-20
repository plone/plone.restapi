.. image:: https://github.com/plone/plone.restapi/workflows/Plone%20RESTAPI%20CI/badge.svg
  :target: https://github.com/plone/plone.restapi/actions?query=workflow%3A%22Plone+RESTAPI+CI%22

.. image:: https://coveralls.io/repos/github/plone/plone.restapi/badge.svg?branch=master
  :target: https://coveralls.io/github/plone/plone.restapi?branch=master

.. image:: https://readthedocs.org/projects/pip/badge
  :target: https://plonerestapi.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/v/plone.restapi.svg
  :target: https://pypi.org/project/plone.restapi/


Introduction
============

``plone.restapi`` is a RESTful hypermedia API for Plone.


Documentation
=============

https://plonerestapi.readthedocs.io/en/latest/


Getting started
===============

A live demo of Plone 6 with the latest ``plone.restapi`` release is available at:

https://demo.plone.org/

An example GET request on the portal root is the following.

.. code-block:: shell

    curl -i https://demo.plone.org/++api++ -H "Accept: application/json"

An example POST request to create a new document is the following.

.. code-block:: shell

    curl -i -X POST https://demo.plone.org/++api++ \
        -H "Accept: application/json" \
        -H "Content-Type: application/json" \
        --data-raw '{"@type": "Document", "title": "My Document"}' \
        --user admin:admin

.. note::

    You will need some kind of API browser application to explore the API.
    You will also need to first obtain a basic authorization token.
    We recommend using `Postman <https://www.postman.com/>`_ which makes it easier to obtain a basic authorization token.


Installation
============

Install ``plone.restapi`` by adding it to your buildout.

.. code-block:: ini

    [buildout]

    # ...

    eggs =
        plone.restapi


…and then running ``bin/buildout``.


Contribute
==========

- Issue Tracker: https://github.com/plone/plone.restapi/issues
- Source Code: https://github.com/plone/plone.restapi
- Documentation: https://plonerestapi.readthedocs.io/en/latest


Examples
========

``plone.restapi`` has been used in production since its first alpha release.
It can be seen in action at the following sites:

- Zeelandia GmbH & Co. KG: https://www.zeelandia.de (by kitconcept GmbH)
- VHS-Ehrenamtsportal: https://vhs-ehrenamtsportal.de (by kitconcept GmbH)
- German Physical Society: https://www.dpg-physik.de (by kitconcept GmbH)
- Universitat Politècnica de Catalunya: https://www.upc.edu/en (by kitconcept GmbH)


Support
=======

If you are having issues, please let us know via the `issue tracker <https://github.com/plone/plone.restapi/issues>`_.

If you require professional support, here is a list of Plone solution providers that contributed significantly to ``plone.restapi`` in the past.

- `kitconcept GmbH <https://kitconcept.com>`_ (Germany)
- `4teamwork <https://www.4teamwork.ch>`_ (Switzerland)
- `CodeSyntax <https://www.codesyntax.com/en>`_ (Spain)


License
=======

The project is licensed under the GPLv2.
