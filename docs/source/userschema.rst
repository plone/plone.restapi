User Schema
===========

.. note::
    This is only available on Plone 5.

Users in Plone have a set of properties defined by a default set of fields like ``fullname``, ``email``, ``portrait``, etc.
These properties define the site user's profile and the user itself via the Plone UI or the site managers can add them in a variety of ways (eg. using PAS plugins.)

These fields are dynamic and customizable by integrators so they do not adhere to a fixed schema interface.
This dynamic schema is exposed by this endpoint in order to build the user's profile form.

Getting the user schema
-----------------------

To get the current user schema make a request to the ``/@userschema`` endpoint::

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/userschema.req

The server will respond with the user schema::

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/userschema.resp
   :language: http

The user schema uses the same serialization as the types JSON schema one.

See :ref:`types-schema` for a detailed documentation about the available field types.
