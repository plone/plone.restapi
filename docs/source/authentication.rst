==============
Authentication
==============

``plone.restapi`` uses Plone PAS for Authentication.

That means that any authentication method supported by an installed PAS Plugin
should work, assuming it's an authentication method that makes sense to use
with an API.

For example, to authenticate using HTTP basic auth, you'd set an
``Authorization`` header:

.. code::

  GET /Plone HTTP/1.1
  Authorization: Basic Zm9vYmFyOmZvb2Jhcgo=
  Accept: application/json

HTTP client libraries usually contain helper functions to produce a proper
``Authorization`` header for you based on given credentials.

Using the ``requests`` library, you'd set up a session with basic auth like
this:

.. code:: python

    import requests

    session = requests.Session()
    session.auth = ('username', 'password')
    session.headers.update({'Accept': 'application/json'})

    response = session.get(url)

Or the same example using ``curl``:

.. code:: python

    curl -u username:password -H 'Accept:application/json' $URL