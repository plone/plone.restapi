Authentication
==============

``plone.restapi`` uses **Plone PAS** for Authentication.

That means that any authentication method supported by an installed PAS Plugin should work, assuming it's an authentication method that makes sense to use with an API.

HTTP Basic Auth
---------------

For example, to authenticate using HTTP basic auth, you'd set an ``Authorization`` header:

.. code::

  GET /Plone HTTP/1.1
  Authorization: Basic Zm9vYmFyOmZvb2Jhcgo=
  Accept: application/json

HTTP client libraries usually contain helper functions to produce a proper ``Authorization`` header for you based on given credentials.

Using the ``requests`` library, you'd set up a session with basic auth like this:

.. code:: python

    import requests

    session = requests.Session()
    session.auth = ('username', 'password')
    session.headers.update({'Accept': 'application/json'})

    response = session.get(url)

Or the same example using ``curl``:

.. code:: python

    curl -u username:password -H 'Accept:application/json' $URL


JSON Web Tokens (JWT)
---------------------

``plone.restapi`` includes a Plone PAS plugin for authentication with JWT. The
plugin is installed automatically when installing the product.

A JWT token can be acquired by posting a user's credentials to the ``@login`` endpoint.

.. example-code::

  .. code-block:: http-request

    POST /@login HTTP/1.1
    Accept: application/json
    Content-Type: application/json

    {
        'login': 'admin',
        'password': 'admin',
    }

  .. code-block:: curl

    curl -i \
    -X POST \
    -H "Accept: application/json" \
    -H "Content-type: application/json" \
    --data-raw '{"login":"admin", "password": "admin"}' \
    http://localhost:8080/Plone/@login

  .. code-block:: python-requests

    requests.post('http://localhost:8080/Plone/@login',
                  headers={'Accept': 'application/json', 'Content-Type': 'application/json'},
                  data='{"login": "admin", "password": "admin"}')


The server responds with a JSON object containing the token.

.. literalinclude:: _json/login.json
   :language: js

The token can now be used in subsequent requests by including it in the
``Authorization`` header with the ``Bearer`` scheme:

.. code::

  GET /Plone HTTP/1.1
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
  Accept: application/json

By default the token will expire after 12 hours and thus must be renewed before
expiration. To renew the token simply post to the ``@login-renew`` endpoint.

.. code::

    POST /@login-renew HTTP/1.1
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
    Accept: application/json

The server returns a JSON object with a new token:

.. literalinclude:: _json/login_renew.json
   :language: js


The ``@logout`` endpoint can be used to invalidate tokens. However, by default
tokens are not persisted on the server and thus can not be invalidated. To enable
token invalidation, activate the ``store_tokens`` option in the PAS plugin. If you
need tokens that are valid indefinitely, you should also disable the use of Plone's
keyring in the PAS plugin (option ``use_keyring``).

The logout request must contain the existing token in the ``Authorization`` header.

.. code::

    POST /@logout HTTP/1.1
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmdWxsbmFtZSI6IiIsInN1YiI6ImFkbWluIiwiZXhwIjoxNDY0MDQyMTAzfQ.aOyvMwdcIMV6pzC0GYQ3ZMdGaHR1_W7DxT0W0ok4FxI
    Accept: application/json

If invalidation succeeds, the server responds with an empty 204 reponse:

.. literalinclude:: _json/logout.json
   :language: js


Permissions
-----------

In order for a user to use the REST API, the ``plone.restapi: Use REST API``
permission is required.

By default, installing the ``plone.restapi:default`` profile will assign this
permission to the ``Anonymous`` role, so everybody is allowed to use the REST
API by default.

If you wish to control in more detail which roles are allowed to use the REST
API, please assign this permission accordingly.

As well as the ``plone.restapi: Use REST API`` permission some of the common
Plone permissions are also required, depending on the particular service.
For example, retrieving a resource using GET will require ``View``, adding an
object using POST will require ``Add portal content``, and so on.

