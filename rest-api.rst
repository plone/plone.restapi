Plone RESTish API
^^^^^^^^^^^^^^^^^

General concepts
****************

Prefix, versioning and dialect
==============================

This API uses a prefix to disambiguate calls to the API from the normal requests. While this is not mandatory for REST APIs, we are forced to do that for a number of reasons:

#. It is necessary to differentiate the request as an API one (think of a dynamic layer)
#. It is necessary to properly support ``PUT`` and ``DELETE`` without falling into the WebDAV codepath.

The prefix also contains information about the version and the dialect of the API: the version is a progressive number (like a package version number, but not tigthly related to it), while the dialect is the format into which the data is passed to the API and returned.

.. note:: Currently the API supports only plain JSON, but we plan to support `JSON-LD`_ in the future.

The prefix has the following schema::

  /++api++<version>/<dialect>/

For example::

  /++api++1/json/


Security
========

.. todo:: check for how oAuth 2 does stuff


Error handling
==============

Our API uses the full range of available HTTP codes to return meaningful information about errors. Each response might contain a JSON body detailing the error that occurred.

Exceptions
----------

In case the server encounters an error, if the authorization level is adequate (like it is done for error pages) then the client receives a full traceback::

  HTTP/1.1 500 Internal Server Error
  Content-Type: application/json
  {
     "type": "AttributeError",
     "exception": "<Item at /foo> has no attribute 'bar'",
     "traceback": "..."
  }

If the authorization level is not enough, the client receives just an error hash::

  HTTP/1.1 500 Internal Server Error
  Content-Type: application/json
  {
     "hash": "..."
  }


Malformed requests
------------------

If the request sent by the client contains errors related to the inputs provided (wrong querystring, wrong JSON body, missing pieces) the API will return a ``400 Bad Request``, with a descriptive text of the error::

  HTTP/1.1 400 Bad Request
  Content-Type: application/json
  {
     "error": "..."
  }

If the request has a content type of ``message/coffeepot``, we will return::

  BREW /plone/++api++1/json HTTP/1.1
  Host: http://nohost
  Content-Type: message/coffeepot
  start


  HTTP/1.1 418 I'm a teapot
  Content-Type: application/json
  {
     "error": "http://tools.ietf.org/html/rfc2324"
  }

.. note:: We might want to restrict this behavior to the 1st of April only, server local time.


Other errors
------------

.. todo: expand

The following code mapping will be used:

``401``
    Missing authentication header/token

``403``
    Authorization level not enough, only for authenticated clients, else ``404``

``405``
    For resources that do not support the HTTP verb (say, a search using ``PUT``)

``423``
    For ``PUT`` and ``PATCH`` requests on a locked resource


Basic content operations
************************

The basic content operations are the CRUD ones (create, retrieve, update, delete).

.. note:: In this section the list of fields is purely an example, this should be expanded more to include correct names and all the properties

To create a document in the portal root, we will do a ``POST`` request (`as recommended by this cookbook <http://restcookbook.com/HTTP%20Methods/put-vs-post/>`_)::

  POST /plone/++api++1/json HTTP/1.1
  Host: http://nohost
  Content-Type: application/json
  {
    "title": "A document",
    "description": "Test",
    "body": "<p>Some <i>HTML</i></p>"
  }

  HTTP/1.1 201 Created
  Location: /plone/++api++1/json/a-document

To retrieve the document we just created we will do::

  GET /plone/++api++1/json/a-document HTTP/1.1
  Host: http://nohost

  HTTP/1.1 200 OK
  Content-Type: application/json
  {
    "title": "A document",
    "description": "Test",
    "body": "<p>Some <i>HTML</i></p>"
  }

To update it we will do::

  PUT /plone/++api++1/json/a-document HTTP/1.1
  Host: http://nohost
  Content-Type: application/json
  {
    "title": "A document",
    "description": "Test",
    "body": "<p>Some <em>semantic HTML</em></p>"
  }

  HTTP/1.1 200 OK
  Content-Type: application/json
  {
    "title": "A document",
    "description": "Test",
    "body": "<p>Some <em>semantic HTML</em></p>"
  }

Notice how we updated all the fields of the content.
This is because, as per `REST cookbook recommendations <http://restcookbook.com/HTTP%20Methods/patch/>`_, ``PUT`` should provide **all the data**.

If we want to do a partial update, e.g. update just the body text, we can use ``PATCH``::

  PATCH /plone/++api++1/json/a-document HTTP/1.1
  Host: http://nohost
  Content-Type: application/json
  {
    "body": "<p>Some <em>semantic HTML</em></p>"
  }

  HTTP/1.1 200 OK
  Content-Type: application/json
  {
    "title": "A document",
    "description": "Test",
    "body": "<p>Some <em>semantic HTML</em></p>"
  }

.. note:: From a pragmatic point of view, differentiating updates between ``PUT`` and ``PATCH`` is inconvenient, and is probably better to just have differential and full updates all under ``PUT``

Finally, to delete our document we will do::

  DELETE /plone/++api++1/json/a-document HTTP/1.1
  Host: http://nohost

  HTTP/1.1 410 Gone
  Location: /plone/++api++1/json/@@listing


Folders
*******

Folders act like basic content in regard to updating their fields (properties).
This means that creating a folder, updating its title and description, and deleting it follows the patterns we saw before (in *Basic content operations*).

However, the folder and, by extension, any folderish content have a very important additional thing, **contained content**.

To keep in line with the `HATEOAS`_ principle, a ``GET`` on the folder should return links to all the contained contents, so that the API is navigable by using links (if you like, *traversable*).

However, this poses an important performance issue.
Imagine you have a folder with 10k contents, it will be very inconvenient to return links to all the 10k contents in the response, because:

#. It will have unmitigable performance issues (even supposing that retrieving the list and rendering the JSON takes zero time, we still need to deliver a huge content)
#. It might not be relevant: we might not be interested in the listing and we will be having a performance issue to return what useless information (atleast for that call)

`The REST cookbook suggests to use pagination <http://restcookbook.com/Resources/pagination/>`_, as it is done on UIs.

Therefore, if we get the folder at ``/plone/my-folder``::

  GET /plone/++api++1/json/my-folder HTTP/1.1
  Host: http://nohost

  HTTP/1.1 200 OK
  Content-Type: application/json
  {
    "title": "A document",
    "description": "Test",
    "@contents": {
      "@list": [
         "http://nohost/++api++1/json/my-folder/document-1",
         "http://nohost/++api++1/json/my-folder/document-2",
         "http://nohost/++api++1/json/my-folder/document-3",
         "http://nohost/++api++1/json/my-folder/document-4",
         "http://nohost/++api++1/json/my-folder/document-5"
      ],
      "@self": "http://nohost/++api++1/json/my-folder/@@contents/0",
      "@next": "http://nohost/++api++1/json/my-folder/@@contents/1",
      "@first": "http://nohost/++api++1/json/my-folder/@@contents/0",
      "@last": "http://nohost/++api++1/json/my-folder/@@contents/5"
    }
  }

We will receive back a special fields containing the initial batch of contained elements, plus links to navigate to other pages where we can retrieve the other contents.

If we traverse to the next page we will then get::

  GET /plone/++api++1/json/my-folder/@@contents/1 HTTP/1.1
  Host: http://nohost

  HTTP/1.1 200 OK
  Content-Type: application/json
  {
    "@contents": {
      "@list": [
         "http://nohost/++api++1/json/my-folder/document-6",
         "http://nohost/++api++1/json/my-folder/document-7",
         "http://nohost/++api++1/json/my-folder/document-8",
         "http://nohost/++api++1/json/my-folder/document-9",
         "http://nohost/++api++1/json/my-folder/document-10"
      ],
      "@self": "http://nohost/++api++1/json/my-folder/@@contents/1",
      "@previous": "http://nohost/++api++1/json/my-folder/@@contents/0",
      "@next": "http://nohost/++api++1/json/my-folder/@@contents/2",
      "@first": "http://nohost/++api++1/json/my-folder/@@contents/0",
      "@last": "http://nohost/++api++1/json/my-folder/@@contents/5"
    }
  }

A few important things to note:

#. The first page has no previous link, and the last will have no next
#. Accessing ``http://nohost/++api++1/json/my-folder/@@contents`` will redirect to the first page

This approach has a few downsides, namely:

#. We still return some potentially useless data
#. The pagination and listing is not configurable (number of elements per batch, sorting), and might result in many calls to retrieve all the content.

Alternative implementation
==========================

An alternative implementation might work similarly, but the ``GET`` would like the ``@@contents`` view only, which in turn would have configurable batching. This might break the `HATEOAS`_ principle a bit but offers pragmatica advantages.

Searching
*********

.. todo:: The author is not quite satisfied with this section. Like, not at all.

Searching should support the following features:

#. Keyword search
#. Full text search
#. Range searches
#. Sorting

It should also:

#. Be available via ``GET`` to support easy caching (`as recommended on stackoverflow <http://stackoverflow.com/questions/5020704/how-to-design-restful-search-filtering>`_)
#. Have a batching mechanism

These requirements restrict us to using either *fake resources* (i.e. ``/search/Title=foo/SearchableText=bar``) or plain old querystrings.

Due to the fact that the latter are more common and more failiar to most web developers, we will go with the latter.

Another choice we face is the use of an internal query language, like it is done by Solr for example, or go with simple lists of indexes to be searched.

We choose the simplest approach, that is use query parameters only::

  GET /plone/++api++1/json/@@search?effective=2014-05-01:date&effective=2014-05-05:date&SearchableText=document&sort_on=created%20desc HTTP/1.1
  Host: http://nohost

  HTTP/1.1 200 OK
  Content-Type: application/json
  [
     "http://nohost/plone/++api++1/json/my-folder/document-1",
     "http://nohost/plone/++api++1/json/my-folder/document-2",
     "http://nohost/plone/++api++1/json/my-folder/document-3",
     "http://nohost/plone/++api++1/json/my-folder/document-4",
     "http://nohost/plone/++api++1/json/my-folder/document-5",
     "http://nohost/plone/++api++1/json/my-folder/document-6",
     "http://nohost/plone/++api++1/json/my-folder/document-7"
  ]

.. note:: This actually turns the search into a faceted search, with mandatory ``AND`` between filters

Contextual search
=================

Search is contextual, which means that while ``/plone/++api++1/json/@@search`` searchs within the full site, ``/plone/++api++1/json/my-folder/@@search`` searches only within ``my-folder``.

Metadata
********

.. todo:: Implement


Workflow
********

.. todo:: Implement


Permissions
***********

.. todo:: Implement


Object introspection
*************

.. todo:: Implement


Global objects
**************

Membership
==========

.. todo:: Implement


Groups
======

.. todo:: Implement


Roles
=====

.. todo:: Implement


Self introspection
==================

.. todo:: Implement




.. _`HATEOAS`: http://restcookbook.com/Basics/hateoas/
.. _`JSON-LD`: http://www.w3.org/TR/json-ld/
