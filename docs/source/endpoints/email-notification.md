---
myst:
  html_meta:
    "description": "Plone allows the user to contact the site owner via a form on the website which sends an email notification."
    "property=og:description": "Plone allows the user to contact the site owner via a form on the website which sends an email notification."
    "property=og:title": "Email Notification"
    "keywords": "Plone, plone.restapi, REST, API, Email, Notification"
---

# Email Notification


## Contact Site Owner (Contact Form)

Plone allows the user to contact the site owner via a form on the website.
This makes sure the site owner does not have to expose their email addresses publicly.
At the same time, it allows the users to reach out to the site owners.

To send an email notification to the site owner, send a `POST` request to the `/@email-notification` endpoint that is available on the site root:

```
POST http://localhost:8080/Plone/@email-notification
Accept: application/json
Content-Type: application/json

{
  "name": "John Doe",
  "from": "john@doe.com",
  "subject": "Hello!",
  "message": "Just want to say hi."
}
```

The `from` and `message` fields are required.
The `subject` and `name` fields are optional.

The server will respond with status {term}`204 No Content` when the email has been sent successfully:

```http
HTTP/1.1 204 No Content
```

## Contact Portal Users

```{note}
This endpoint is NOT implemented yet.
```

To send an email notification to another user of the portal, send a `POST` request to the `/@email-notification` endpoint on a particular user, for example, the admin user:

```
POST http://localhost:8080/Plone/@users/admin/@email-notification
Accept: application/json
Content-Type: application/json

{
  "name": "John Doe",
  "from": "john@doe.com",
  "subject": "Hello!",
  "message": "Just want to say hi."
}
```

```{note}
When using "email as login", we strongly recommend to also enable the "Use UUID user ids" setting in the security control panel to obfuscate the email in the user endpoint URL.
Otherwise the `@users` endpoint will expose the email addresses of all your users.
```
