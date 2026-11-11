---
myst:
  html_meta:
    "description": "A hypermedia API provides an entry point to the API, which contains hyperlinks the clients can follow."
    "property=og:description": "A hypermedia API provides an entry point to the API, which contains hyperlinks the clients can follow."
    "property=og:title": "Introduction"
    "keywords": "Plone, plone.restapi, REST, API, Introduction"
---

# Introduction

```{sidebar} API Browser Guide
**It can make your life easier** if you use some kind of **API browser application** to **explore the API** when diving into this documentation.

- We recommend using the free [Postman](https://www.postman.com/).
- For onboarding, take a look at **our guide {ref}`exploring-api-postman-onboarding`**.
```

A hypermedia API provides an entry point to the API, which contains hyperlinks the clients can follow.
Just like a person who visits a regular website, if they know the initial URL, then they can follow hyperlinks to navigate through the site.
This has the advantage that the client only needs to understand how to detect and follow links.
The URLs (apart from the initial entry point) and other details of the API can change without breaking the client.

The entry point to the Plone RESTful API is the portal root.
The client can send an HTTP request for a {term}`REST` API response by setting the `"Accept"` HTTP header to `"application/json"`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/siteroot.req
```

This uses {ref}`content negotiation <restapi-content-negotiation-label>`.

The server will then respond with the portal root in the JSON format:

```{literalinclude} ../../src/plone/restapi/tests/http-examples/siteroot.resp
:language: http
```

`@id`
: A unique identifier for resources (IRIs).
  The `@id` property can be used to navigate through the web API by following the links.

`@type`
: Sets the data type of a node or typed value.

`items`
: A list that contains all objects within that resource.

A client application can "follow" the links (by calling the `@id` property) to other resources.
This lets a developer build a loosely coupled client that does not break if some URLs change.
Only the entry point of the entire API (in our case the portal root) needs to be known in advance.

Here is another example, this time showing a request and response for a document.
Click {guilabel}`http`, {guilabel}`curl`, {guilabel}`httpie`, or {guilabel}`python-requests` to show the syntax of the request for that client:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/document.req
```

```{literalinclude} ../../src/plone/restapi/tests/http-examples/document.resp
:language: http
```

(restapi-content-negotiation-label)=

## Content Negotiation

[Content negotiation](https://datatracker.ietf.org/doc/html/rfc7231#section-5.3) is a mechanism defined in the [HTTP specification](https://datatracker.ietf.org/doc/html/rfc7231) that makes it possible to serve different versions of a document (or more generally, a resource representation) at the same URI, so that user agents can specify which version fit their capabilities the best.

The user agent (or the REST consumer) can ask for a specific representation by providing an `Accept` HTTP header that lists acceptable media types, such as JSON:

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
