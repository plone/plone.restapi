Add-ons
========

Addon product records can be addressed through the ``@addons`` endpoint on the
Plone site. In order to address a specific record, the profile id has to be
passed as a path segment (e.g. `/plone/@addons/plone.session`).

Reading or writing addons metadata require the ``cmf.ManagePortal``
permission.

Reading add-ons records
-----------------------

Reading a single record:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_get.req

Example Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_get.resp
   :language: http


Listing add-ons records
-----------------------

A list of all add-ons in the portal can be retrieved by
sending a GET request to the @addons endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_get_list.req

Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_get_list.resp
   :language: http

The following fields are returned:

- @id: hypermedia link to the control panel
- id: the name of the add-on package
- title: the friendly name of the add-on package
- description: description of the add-on
- version: the current version of the add-on
- is_installed: is the add-on installed?
- has_uninstall_profile: does the add-on have an uninstall profile


Installing an addon
-------------------

An individual addon can be installed by issuing a ``POST`` to the given URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_install.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_install.resp
   :language: http


Uninstalling an addon
---------------------

An individual addon can be uninstalled by issuing a ``POST`` to the given URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_uninstall.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_uninstall.resp
   :language: http


Upgrading an addon
-------------------

An individual addon can be upgraded by issuing a ``POST`` to the given URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_upgrade.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_upgrade.resp
   :language: http
