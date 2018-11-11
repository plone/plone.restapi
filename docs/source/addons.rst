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

The addons listing uses a batched method to access all addons.
See :doc:`/batching` for more details on how to work with batched results.


..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_get_list.req

Example Response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_get_list.resp
   :language: http


Installing an addon
-------------------

An individual addon can be installed by issuing a ``POST`` to the given URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/addons_install.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/addons_install.resp
   :language: http


Uninstalling an addon
-------------------

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
