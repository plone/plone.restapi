Email Notification
==================

Contact Site Owner aka Contact Form
-----------------------------------

Plone allows the user to contact the site owner via a form on the website.
This makes sure the site owner does not have to expose their email addresses publicly and at the same time allow the users to reach out to the site owners.

To send an email notification to the site owner, send a POST request to the ``/@email-notification`` endpoint that is available on the site root::

    POST http://localhost:8080/Plone/@email-notification
    Accept: application/json
    Content-Type: application/json

    {
      'name': 'John Doe',
      'from': 'john@doe.com',
      'subject': 'Hello!',
      'message': 'Just want to say hi.'
    }

The 'from' and 'message' fields are required. The 'subject' and 'name' fields are optional.

The server will respond with status :term:`204 No Content` when the email has been sent successfully::

    HTTP/1.1 204 No Content


Contact Portal Users
--------------------

To send an email notification to another user of the portal, send a POST request to the ``/@email-notification`` endpoint on a particular user (e.g. the admin user)::

    POST http://localhost:8080/Plone/@users/admin/@email-notification
    Accept: application/json
    Content-Type: application/json

    {
      'name': 'John Doe',
      'from': 'john@doe.com',
      'subject': 'Hello!',
      'message': 'Just want to say hi.'
    }

