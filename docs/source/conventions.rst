Conventions
===========

Nouns vs Verbs
--------------

Rule: Use nouns to represent resources.

Do::

  /my-folder
  /@registry
  /@types

Don't::

  /createFolder
  /deleteDocument
  /updateEvent

Reason:

RESTful URI should refer to a resource that is a thing (noun) instead of
referring to an action (verb) because nouns have properties as verbs do
not. The REST architectural principle uses HTTP verbs to interact with
resources.

Though, there is an exception to that rule, verbs can be used for
specific actions or calculations, .e.g.::

  /login
  /logout
  /move-to
  /reset-password


Singluar vs Plural
------------------

Rule: Use plural resources.

Do::

  /users
  /users/21

Don't::

  /user
  /user/21

Reason:

If you use singular for a collection like resource (e.g. "/user" to
retrieve a list of all users) it feels wrong. Mixing singular and plural
is confusing (e.g. user "/users" for retrieving users and "/user/21" to
retrieve a single user).


Attribute names in URIs
-----------------------

Rule: Use hyphens to improve readability of URIs.

Do::

    /users/noam/reset-password

Don't::

    /users/noam/resetPassword
    /users/noam/ResetPassword
    /users/noam/reset_password

Reason:



Upper vs. Lowercase
-------------------

Rule: Use lowercase letters in URIs.

Do::

  http://example.com/my-folder/my-document

Don't::

  http://example.com/My-Folder/My-Document

Reason: RFC 3986 defines URIs as case-sensitive except for the scheme
and host components. e.g.

Those two URIs are equivalent::

    http://example.org/my-folder/my-document
    HTTP://EXAMPLE.ORG/my-folder/my-document

While this one is not equivalent to the two URIs above::

    http://example.org/My-Folder/my-document

To avoid confusion we always use lowercase letters in URIs.


Versioning
----------

Versioning APIs does make a lot of sense for public API services. 
Especially if an API provider needs to ship different versions of the API at the same time. 
Though, Plone already has a way to version packages and it currently does not make sense for us to expose that information via the API.
We will always just ship one version of the API at a time and we are usually in full control over the backend and the frontend.
