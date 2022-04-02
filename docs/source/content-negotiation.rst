Content Negotiation
===================

`Content negotiation <http://tools.ietf.org/html/rfc7231#section-5.3>`_ is a mechanism defined in the `HTTP specification <http://tools.ietf.org/html/rfc7231>`_ that makes it possible to serve different versions of a document (or more generally, a resource representation) at the same URI, so that user agents can specify which version fit their capabilities the best.

The user agent (or the REST consumer) can ask for a specific representation by providing an Accept HTTP header that lists acceptable media types (e.g. JSON)::

  GET /
  Accept: application/json

The server is then able to supply the version of the resource that best fits the user agent's needs.
This is reflected in the Content-Type header::

  HTTP 200 OK
  Content-Type: application/json

  {
    'data': ...
  }