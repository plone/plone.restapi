---
myst:
  html_meta:
    "description": "Single-use form tokens that make bots wait before they can submit a form."
    "property=og:description": "Single-use form tokens that make bots wait before they can submit a form."
    "property=og:title": "Form Token"
    "keywords": "Plone, plone.restapi, REST, API, Form, Token, Spam"
---

# Form Token

Form tokens make bots wait before they can submit a form, without bothering visitors with a puzzle.
A form gets a token when it is shown and sends it along when it is submitted.
The backend only accepts a token once, and only when it is old enough: bots post at once, people need time to fill in a form.
This works next to a captcha, if the form has one.

The {doc}`email-notification` endpoint checks the token of the contact form.
Add-ons can check tokens for their own forms with `plone.restapi.form_token.verify_token`.

## Configuration

Form tokens are kept in memcached, because issuing one is a write on a `GET` request.
They are only enabled when [pymemcache](https://pypi.org/project/pymemcache/) is installed, for example with the `token` extra of `plone.restapi`, and these environment variables are set:

`FORM_TOKEN_MEMCACHE`
:   The memcached servers, separated by spaces, like `memcached:11211`.
    Without it, forms work as before, without tokens.

`FORM_TOKEN_MIN_AGE`
:   The number of seconds before a token can be used, 15 by default.

`FORM_TOKEN_LIFETIME`
:   The number of seconds a token stays valid, 3600 by default.

## Get a token

To get a token, send a `GET` request to the `@form-token` endpoint:

```
GET http://localhost:8080/Plone/@form-token
Accept: application/json
```

The response has the token and the number of seconds the form should wait before it uses it:

```json
{
  "token": "Tz6m1yIFEdmVq3kBkzRPy8Fk3Ngvq2qXIgVbCrfM5yc",
  "min_age": 15
}
```

The response has `Cache-Control: no-store, private`, because each visitor needs a token of their own.
When form tokens are not enabled, or memcached cannot store the token, the server responds with status {term}`503 Service Unavailable`.
Without pymemcache, the endpoint does not exist.

## Use a token

Send the token as `form_token` with the form:

```
POST http://localhost:8080/Plone/@email-notification
Accept: application/json
Content-Type: application/json

{
  "from": "john@doe.com",
  "message": "Just want to say hi.",
  "form_token": "Tz6m1yIFEdmVq3kBkzRPy8Fk3Ngvq2qXIgVbCrfM5yc"
}
```

A token is used up by every submission, also one that fails, so get a new token after each one.
A missing, unknown, used or too new token gives a {term}`400 Bad Request` with the message `Invalid request.`.
A token that is used too early is logged as `Spam blocked: reason=early-token form=<form>`, so you can count them.
