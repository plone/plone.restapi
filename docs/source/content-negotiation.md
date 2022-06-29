---
html_meta:
  "description": "Content negotiation is a mechanism defined in the HTTP specification that makes it possible to serve different versions of a document (or more generally, a resource representation) at the same URI, so that user agents can specify which version fit their capabilities the best."
  "property=og:description": "Content negotiation is a mechanism defined in the HTTP specification that makes it possible to serve different versions of a document (or more generally, a resource representation) at the same URI, so that user agents can specify which version fit their capabilities the best."
  "property=og:title": "Content Negotiation"
  "keywords": "Plone, plone.restapi, REST, API, Content, Negotiation"
---

# Content Negotiation

[Content negotiation](https://datatracker.ietf.org/doc/html/rfc7231#section-5.3) is a mechanism defined in the [HTTP specification](https://datatracker.ietf.org/doc/html/rfc7231) that makes it possible to serve different versions of a document (or more generally, a resource representation) at the same URI, so that user agents can specify which version fit their capabilities the best.

The user agent (or the REST consumer) can ask for a specific representation by providing an `Accept` HTTP header that lists acceptable media types (e.g., JSON):

```
GET /
Accept: application/json
```

The server is then able to supply the version of the resource that best fits the user agent's needs.
This is reflected in the `Content-Type` header:

```
HTTP 200 OK
Content-Type: application/json

{
  'data': ...
}
```
