---
myst:
  html_meta:
    "description": "plone.restapi uses PlonePAS for authentication."
    "property=og:description": "`plone.restapi uses PlonePAS for authentication."
    "property=og:title": "Authentication"
    "keywords": "Plone, plone.restapi, REST, API, Authentication, "
---

# Authentication

`plone.restapi` uses [`PlonePAS`](https://github.com/plone/Products.PlonePAS) for authentication.

That means that any authentication method supported by an installed PAS plugin should work, assuming it's an authentication method that makes sense to use with an API.

For example, to authenticate using HTTP basic auth, you'd set an `Authorization` header:

```http
GET /Plone HTTP/1.1
Authorization: Basic Zm9vYmFyOmZvb2Jhcgo=
Accept: application/json
```

HTTP client libraries usually contain helper functions to produce a proper `Authorization` header for you based on given credentials.

Using the `requests` library, you would set up a session with basic authentication as follows:

```python
import requests

session = requests.Session()
session.auth = ('username', 'password')
session.headers.update({'Accept': 'application/json'})

response = session.get(url)
```

Or the same example using `curl`:

```bash
curl -u username:password -H 'Accept:application/json' $URL
```


## JSON Web Tokens (JWT)

`plone.restapi` includes a Plone PAS plugin for authentication with JWT.
The plugin is installed automatically when installing the product.


### Acquiring a token (@login)

A JWT token can be acquired by posting a user's credentials to the `@login` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/jwt_login.req
```

The server responds with a JSON object containing the token:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/jwt_login.resp
:language: http
```


### Authenticating with a token

The token can now be used in subsequent requests by including it in the `Authorization` header with the `Bearer` scheme:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/jwt_logged_in.req
```


### Renewing a token (@login-renew)

By default, the token will expire after 12 hours, and thus must be renewed before expiration.
To renew the token, `POST` to the `@login-renew` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/jwt_login_renew.req
```

The server returns a JSON object with a new token:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/jwt_login_renew.resp
:language: http
```


### Invalidating a token (@logout)

The `@logout` endpoint can be used to invalidate tokens.
However by default tokens are not persisted on the server and thus can not be invalidated.
To enable token invaldiation, activate the `store_tokens` option in the PAS plugin.
If you need tokens that are valid indefinitely you should also disable the use of Plone's keyring in the PAS plugin (option `use_keyring`).

The logout request must contain the existing token in the `Authorization` header:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/jwt_logout.req
```

If invalidation succeeds, the server responds with an empty 204 response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/jwt_logout.resp
:language: http
```


## Permissions

In order for a user to use the REST API, the `plone.restapi: Use REST API` permission is required.

By default, installing the `plone.restapi:default` profile will assign this permission to the `Anonymous` role.
Everybody is allowed to use the REST API by default.

If you wish to control in more detail which roles are allowed to use the REST API, please assign this permission accordingly.

As well as the `plone.restapi: Use REST API` permission, some of the common Plone permissions are also required, depending on the particular service.
For example, retrieving a resource using `GET` will require `View`.
Adding an object using `POST` will require `Add portal content`.

In order to modify or override this behavior, if your custom service class inherits from `plone.restapi.services.Service`, override the method `check_permission` and add your custom checks accordingly.
