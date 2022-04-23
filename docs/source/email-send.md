---
html_meta:
  "description": ""
  "property=og:description": ""
  "property=og:title": ""
  "keywords": "Plone, plone.restapi, REST, API"
---

# Email Send


## Send Mail to Arbitrary Addresses

To send an email to an arbitrary email address, send a `POST` request to the `/@email-send` endpoint that is available on the site root:

```
POST http://localhost:8080/Plone/@email-send
Accept: application/json
Content-Type: application/json

{
  "name": "John Doe",
  "from": "john@doe.com",
  "to": "jane@doe.com",
  "subject": "Hello!",
  "message": "Just want to say hi."
}
```

This endpoint is controlled via the `Use mailhost services` permission, the default one in Zope.

The `to`, `from`, and `message` fields are required.
The `subject` and `name` fields are optional.

The server will respond with status {term}`204 No Content` when the email has been sent successfully:

```http
HTTP/1.1 204 No Content
```
