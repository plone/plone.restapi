.. include:: /alert-noindex.rst

********
Security
********

To provide security, the current most popular approach seems to be `JSON Web Tokens <http://self-issued.info/docs/draft-ietf-oauth-json-web-token.html>`_.

In short, the functioning is quite simple:

 * The client authenticates with credentials on the server and gets back a token
 * The client can then provide the token at every request (a little bit like it's done by HTTP basic auth, except the password isn't revealed)

How it works
------------

Suppose we want to retrieve a page that is currently private (and will, in standard Plone, redirect to the login page)::


  GET /++api++1/front-page/ HTTP/1.1
  Host: nohost
  Accept: application/json



  401 Unauthorized HTTP/1.1
  Content-Type: application/json

  {
    "@error": {
      "type": "Unauthorized"
    }
    "@actions": {
      "login": {
      "@href": "http://nohost/++api++1/++actions++login/",
        "@template": {
           "username": {
             "@type": "string"
           },
           "password": {
             "@type": "string"
           }
        }
      }
    }
  }

The response tells us that we are not authorized, and that to gain authorization we must provide a username and a password::

  POST /++api++1/++actions++login/ HTTP/1.1
  Host: nohost
  Content-Type: application/json

  {
    "username": "admin",
    "password": "admin"
  }


  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@response": {
       "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEzODY4OTkxMzEsImlzcyI6ImppcmE6MTU0ODk1OTUiLCJxc2giOiI4MDYzZmY0Y2ExZTQxZGY3YmM5MGM4YWI2ZDBmNjIwN2Q0OTFjZjZkYWQ3YzY2ZWE3OTdiNDYxNGI3MTkyMmU5IiwiaWF0IjoxMzg2ODk4OTUxfQ.uKqU9dTB6gKwG6jQCuXYAiMNdfNRw98Hw_IWuA5MaMo"
    }
  }

The response, as we can see, gave us a token. With this token, we can now proceed and obtain the page::

  GET /++api++1/front-page/ HTTP/1.1
  Host: nohost
  Accept: application/json
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjEzODY4OTkxMzEsImlzcyI6ImppcmE6MTU0ODk1OTUiLCJxc2giOiI4MDYzZmY0Y2ExZTQxZGY3YmM5MGM4YWI2ZDBmNjIwN2Q0OTFjZjZkYWQ3YzY2ZWE3OTdiNDYxNGI3MTkyMmU5IiwiaWF0IjoxMzg2ODk4OTUxfQ.uKqU9dTB6gKwG6jQCuXYAiMNdfNRw98Hw_IWuA5MaMo

  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@href": "http://nohost/++api++1/front-page/",
    "@info": {
      "portal_type": {
        "@href": "http://nohost/++api++1/++globals++types/Page",
        "@info": {
          "id": "Page"
        }
      },
      "created": "2014-04-22T05:33:58.930Z"
    },
    "@actions": {
      "workflow": {
        "@href": "http://nohost/++api++1/front-page/++actions++workflow/",
        "@template": {
           "type": {
             "@type": "string",
             "@choices": [
                "submit",
                "publish"
             ]
           }
        }
      }
    },
    "@data": {
      "short_name": "yet-another-page",
      "title": "Yet another page",
      "description": null,
      "text": "<p>I've got a fever, and the only cure is <b>more</b> JSON!</p>",
      "allow_discussion": null,
      "exclude_from_navigation": false,
      "table_of_contents": false,
      "tags": [],
      "language": null,
      "related_items": [],
      "effective": null,
      "expires": null,
      "creator": {
        "@href": "http://nohost/++api++1/++globals++users/admin"
        "@info": {
          "id": "admin"
        }
      },
      "contributors": [],
      "rights": ""
    },
    "@template": {
      "@href": "http://nohost/++api++1/++globals++types/Page/@@template"
    }
  }


Basic authentication fallback
-----------------------------

As a fallback, basic authentication is also supported by the API: in this case, there is no need to pass from the login page but the credentials can be provided via the ``Authorization`` header.
