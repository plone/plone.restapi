---
myst:
  html_meta:
    "description": "A list of HTTP status codes that are used in plone.restapi."
    "property=og:description": "A list of HTTP status codes that are used in plone.restapi."
    "property=og:title": "HTTP Status Codes"
    "keywords": "Plone, plone.restapi, REST, API, HTTP, Status, Codes"
---

# HTTP Status Codes

This is the list of HTTP status codes that are used in `plone.restapi`.
Here is a [full list of all HTTP status codes](https://en.wikipedia.org/wiki/List_of_HTTP_status_codes).

## Error Response Format (RFC 7807)

All error responses follow [RFC 7807 (Problem Details for HTTP APIs)](https://tools.ietf.org/html/rfc7807) format.

### OpenAPI Schema

For OpenAPI/Swagger documentation, use the `RFC7807Error` schema:

```yaml
RFC7807Error:
  type: object
  properties:
    type:
      type: string
      format: uri
      description: A URI reference that identifies the problem type.
      example: /problem-types/validation-error
    title:
      type: string
      description: A short, human-readable summary of the problem type.
      example: Bad Request
    status:
      type: integer
      description: The HTTP status code.
      example: 400
    detail:
      type: string
      description: A human-readable explanation specific to this occurrence of the problem.
      example: Login and password must be provided in body.
    instance:
      type: string
      format: uri
      description: The request path that caused the error.
      example: /plone/@login
    message:
      type: string
      description: "[DEPRECATED] Human-readable error message. Same as 'detail'. Will be removed in future releases."
      example: Login and password must be provided in body.
      deprecated: true
    context:
      type: string
      format: uri
      description: "[DEPRECATED] URL of the closest visible context. Will be removed in future releases."
      example: https://example.com/plone
      deprecated: true
    error_type:
      type: string
      description: "[DEPRECATED] Legacy field for backwards compatibility. Will be removed in future releases."
      example: Missing credentials
      deprecated: true
    traceback:
      type: array
      items:
        type: string
      description: "[DEPRECATED] Stack trace for debugging. Only visible to users with ManagePortal permission. Will be removed in future releases."
      deprecated: true
  required:
    - type
    - title
    - status
    - detail
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `type` | string (URI) | A relative URI that identifies the problem type |
| `title` | string | A short, human-readable summary of the problem |
| `status` | integer | The HTTP status code |
| `detail` | string | A human-readable explanation specific to this occurrence |
| `instance` | string | The request path that caused the error |

### Backwards Compatible Fields (DEPRECATED)

For backwards compatibility, error responses also include these fields.
**They will be removed in future releases.**

| Field | Type | Description |
|-------|------|-------------|
| `message` | string | **DEPRECATED** - The error message (same as `detail`) |
| `context` | string | **DEPRECATED** - URL of the closest visible context |
| `traceback` | array | **DEPRECATED** - Stack trace (only visible to users with `ManagePortal` permission) |
| `error_type` | string | **DEPRECATED** - Legacy error type identifier |

### Backwards Compatibility Configuration

By default, deprecated fields are included in error responses for backwards compatibility.
You can disable this to get a cleaner RFC 7807-only response:

```python
from plone.restapi.problem_types import set_backwards_compat

# Disable deprecated fields in error responses
set_backwards_compat(False)

# Re-enable (default)
set_backwards_compat(True)
```

When disabled, error responses will only contain RFC 7807 fields:
- `type`, `title`, `status`, `detail`, `instance`

When enabled (default), error responses will also include:
- `message`, `context`, `error_type`, `traceback` (deprecated)

### Example Responses

**400 Bad Request (Validation Error):**

```json
{
    "type": "/problem-types/validation-error",
    "title": "Bad Request",
    "status": 400,
    "detail": "Login and password must be provided in body.",
    "instance": "/plone/@login",
    "message": "Login and password must be provided in body.",
    "error_type": "Missing credentials"
}
```

**401 Unauthorized (Invalid Credentials):**

```json
{
    "type": "/problem-types/invalid-credentials",
    "title": "Unauthorized",
    "status": 401,
    "detail": "Wrong login and/or password.",
    "instance": "/plone/@login",
    "message": "Wrong login and/or password.",
    "error_type": "Invalid credentials"
}
```

**403 Forbidden:**

```json
{
    "type": "/problem-types/forbidden",
    "title": "Forbidden",
    "status": 403,
    "detail": "You do not have permission to access this resource.",
    "instance": "/plone/document",
    "message": "You do not have permission to access this resource."
}
```

**404 Not Found:**

```json
{
    "type": "/problem-types/resource-not-found",
    "title": "Not Found",
    "status": 404,
    "detail": "The requested resource could not be found.",
    "instance": "/plone/non-existent",
    "message": "The requested resource could not be found."
}
```

### Problem Types

| Problem Type | URI | HTTP Status |
|--------------|-----|-------------|
| Validation Error | `/problem-types/validation-error` | 400 |
| Missing Credentials | `/problem-types/missing-credentials` | 400 |
| Invalid Credentials | `/problem-types/invalid-credentials` | 401 |
| Unauthorized | `/problem-types/unauthorized` | 401 |
| Forbidden | `/problem-types/forbidden` | 403 |
| Resource Not Found | `/problem-types/resource-not-found` | 404 |
| Conflict | `/problem-types/conflict` | 409 |
| Internal Error | `/problem-types/internal-error` | 500 |

## HTTP Status Codes

```{glossary}
:sorted: true

2xx Success
    This class of status codes indicates the action requested by the client was received, understood, accepted, and processed successfully.

200 OK
    Standard response for successful HTTP requests.
    The actual response will depend on the request method used.
    In a `GET` request, the response will contain an entity corresponding to the requested resource.
    In a `POST` request, the response will contain an entity describing or containing the result of the action.

201 Created
    The request has been fulfilled and resulted in a new resource being created.

204 No Content
    The server successfully processed the request, but is not returning any content.
    Usually used as a response to a successful `DELETE` request.

4xx Client Error
    The `4xx` class of status codes is intended for cases in which the client seems to have errored.

400 Bad Request
    The server cannot or will not process the request due to something that is perceived to be a client error, such as malformed request syntax, invalid request message framing, or deceptive request routing.

401 Unauthorized
    Similar to {term}`403 Forbidden`, but specifically for use when authentication is required and has failed or has not yet been provided.
    The response must include a `WWW-Authenticate` header field containing a challenge applicable to the requested resource.

403 Forbidden
    The request was a valid request, but the server is refusing to respond to it.
    Unlike a {term}`401 Unauthorized` response, authenticating will make no difference.

404 Not Found
    The requested resource could not be found but may be available again in the future.
    Subsequent requests by the client are permissible.

405 Method Not Allowed
    A request method is not supported for the requested resource; for example, a `GET` request on a form which requires data to be presented via `POST`, or a `PUT` request on a read-only resource.

409 Conflict
    Indicates that the request could not be processed because of conflict in the request, such as an edit conflict in the case of multiple updates.

5xx Server Error
500 Internal Server Error
    The server failed to fulfill an apparently valid request.
```

