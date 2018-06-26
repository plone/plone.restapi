Upgrade Guide
=============

This upgrade guide lists all breaking changes in plone.restapi and explains the necessary steps that are needed to upgrade to the lastest version.


Upgrading to plone.restapi 3.x
------------------------------

Image scales
^^^^^^^^^^^^

Image download URLs and image scale URLs are created using the UID based url formats. This allows Plone to create different URLs when the image changes and thus ensuring caches are updated.

Old Response:: 

     {
       "icon": {
         "download": "http://localhost:55001/plone/image/@@images/image/icon",
         "height": 32,
         "width": 24
       },
       "large": {
         "download": "http://localhost:55001/plone/image/@@images/image/large",
         "height": 768,
         "width": 576
       },
       ...
      }

New Response::

     {
       "icon": {
         "download": "http://localhost:55001/plone/image/@@images/8eed3f80-5e1f-4115-85b8-650a10a6ca84.png",
         "height": 32,
         "width": 24
       },
       "large": {
         "download": "http://localhost:55001/plone/image/@@images/0d1824d1-2672-4b62-9277-aeb220d3bf15.png",
         "height": 768,
         "width": 576
       },
      ...
      }
     

@sharing endpoint
^^^^^^^^^^^^^^^^^

The ``available_roles`` property in the response to a GET request to the
``@sharing`` endpoint has changed: Instead of a flat list of strings, it now
contains a list of dicts, with the role ID and their translated title:

Old Response::

  HTTP/1.1 200 OK
  Content-Type: application/json
  
  {
    "available_roles": [
      "Contributor",
      "Editor",
      "Reviewer",
      "Reader"
    ],
    "entries": [
        "..."
    ],
    "inherit": true
  }


New Response::

  HTTP/1.1 200 OK
  Content-Type: application/json
  
  {
    "available_roles": [
      {
        "id": "Contributor",
        "title": "Can add"
      },
      {
        "id": "Editor",
        "title": "Can edit"
      },
      {
        "id": "Reader",
        "title": "Can view"
      },
      {
        "id": "Reviewer",
        "title": "Can review"
      }
    ],
    "entries": [
        "..."
    ],
    "inherit": true
  }


Custom Content Deserializers
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you have implemented custom content deserializers, you have to handle the
new ``create`` keyword in the ``__call__`` method, which determines if deserialization
is performed during object creation or while updating an object.

Deserializers should only fire an ``IObjectModifiedEvent`` event if an object
has been updated. They should not fire it, when a new object has been created.

See `Dexterity content deserializer <https://github.com/plone/plone.restapi/blob/master/src/plone/restapi/deserializer/dxcontent.py>`_ for an example.


Upgrading to plone.restapi 2.x
------------------------------

plone.restapi 2.0.0 converts all datetime, DateTime and time to UTC before serializing.
The translations endpoint becomes "expandable", which introduces the following breaking changes.

Translations
^^^^^^^^^^^^

When using the `@translations` endpoint in plone.restapi 1.x, the endpoint returned a `language` key
with the content object's language and a `translations` key with all its translations.

Now, as the endpoint is expandable we want the endpoint to behave like the other expandable endpoints.
As top level information we only include the name of the endpoint on the `@id` attribute and the actual
translations of the content object in an attribute called `items`.

This means that now the JSON response to a GET request to the :ref:`translations` endpoint does not
include anymore the language of the actual content item and the translations in an attribute called
`items` instead of `translations`.

Old response::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/en/test-document",
    "language": "en",
    "translations": [
      {
        "@id": "http://localhost:55001/plone/es/test-document",
        "language": "es"
      }
    ]
  }

New response::

  HTTP/1.1 200 OK
  Content-Type: application/json

  {
    "@id": "http://localhost:55001/plone/en/test-document/@translations",
    "items": [
      {
        "@id": "http://localhost:55001/plone/es/test-document",
        "language": "es"
      }
    ]
  }


Upgrading to plone.restapi 1.0b1
--------------------------------

In plone.restapi 1.0b1 the 'url' attribute on the :ref:`navigation` and :ref:`breadcrumbs` endpoint was renamed to '@id' to be consistent with other links/URLs used in
plone.restapi.

The JSON response to a GET request to the :ref:`breadcrumbs` endpoint changed from using the 'url' attribute for 'items'::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/front-page/@breadcrumbs",
      "items": [
        {
          "title": "Welcome to Plone",
          "url": "http://localhost:55001/plone/front-page"
        }
      ]
    }

to using the '@id' for the URL of 'items'::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/front-page/@breadcrumbs",
      "items": [
        {
          "@id": "http://localhost:55001/plone/front-page",
          "title": "Welcome to Plone"
        }
      ]
    }

The JSON response to a GET request to the :ref:`navigation` endpoint changed from using the 'url' attribute for 'items'::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/front-page/@navigation",
      "items": [
        {
          "title": "Home",
          "url": "http://localhost:55001/plone",
        },
        {
          "title": "Welcome to Plone",
          "url": "http://localhost:55001/plone/front-page"
        }
      ]
    }

to using the '@id' for the URL of 'items'::

    HTTP/1.1 200 OK
    Content-Type: application/json

    {
      "@id": "http://localhost:55001/plone/front-page/@navigation",
      "items": [
        {
          "@id": "http://localhost:55001/plone",
          "title": "Home"
        },
        {
          "@id": "http://localhost:55001/plone/front-page",
          "title": "Welcome to Plone"
        }
      ]
    }

The expansion mechanism is also affected by this change when :ref:`navigation` or :ref:`breadcrumbs` endpoints are expanded.

From using 'url' in the breadcrumb 'items'::

    {
      "@components": {
        "breadcrumbs": {
          "@id": "http://localhost:55001/plone/front-page/@breadcrumbs",
          "items": [
            {
              "title": "Welcome to Plone",
              "url": "http://localhost:55001/plone/front-page"
            }
          ]
        },
        "navigation": {
          "@id": "http://localhost:55001/plone/front-page/@navigation",
          "items": [
            {
              "title": "Home",
              "url": "http://localhost:55001/plone",
            },
            {
              "title": "Welcome to Plone",
              "url": "http://localhost:55001/plone/front-page"
            }
          ]
        },
        ...
    }

to using '@id' in the breadcrumb 'items'::

    {
      "@components": {
        "breadcrumbs": {
          "@id": "http://localhost:55001/plone/front-page/@breadcrumbs",
          "items": [
            {
              "@id": "http://localhost:55001/plone/front-page",
              "title": "Welcome to Plone"
            }
          ]
        },
        "navigation": {
          "@id": "http://localhost:55001/plone/front-page/@navigation",
          "items": [
            {
              "@id": "http://localhost:55001/plone",
              "title": "Home"
            },
            {
              "@id": "http://localhost:55001/plone/front-page",
              "title": "Welcome to Plone"
            }
          ]
        },
        ...
    }

Changelog::

- Rename 'url' attribute on navigation / breadcrumb to '@id'. [timo]

Pull Request:

- https://github.com/plone/plone.restapi/pull/459


Upgrading to plone.restapi 1.0a25
---------------------------------

plone.restapi 1.0a25 introduced three breaking changes:

- Remove @components navigation and breadcrumbs. Use top level @navigation and
  @breadcrumb endpoints instead. [timo]

- Remove "sharing" attributes from GET response. [timo,jaroel]

- Convert richtext using .output_relative_to. Direct conversion from RichText
  if no longer supported as we *always* need a context for the ITransformer. [jaroel]

Remove @components endpoint
^^^^^^^^^^^^^^^^^^^^^^^^^^^

plone.restapi 1.0a25 removed the @components endpoint which used to provide a
:ref:`navigation` and a :ref:`breadcrumbs` endpoint.

Instead of using "@components/navigation"::

  http://localhost:8080/Plone/@components/navigation

Use just "@navigation"::

  http://localhost:8080/Plone/@navigation

Instead of using "@components/breadcrumbs"::

  http://localhost:8080/Plone/@components/breadcrumbs

Use just "@breadcrumbs"::

  http://localhost:8080/Plone/@breadcrumbs

Changelog::

- Remove @components navigation and breadcrumbs. Use top level @navigation and @breadcrumb endpoints instead. [timo]

Pull Request:

- https://github.com/plone/plone.restapi/pull/425


Remove "sharing" attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The "sharing" attribute was removed from all content GET responses::

  "sharing": {
    "@id": "http://localhost:55001/plone/collection/@sharing",
    "title": "Sharing"
  },

Use the :ref:`sharing` endpoint that can be expanded instead.

Changelog::

- Remove "sharing" attributes from GET response. [timo,jaroel]

Pull Request:

- https://github.com/plone/plone.restapi/commit/1b5e9e3a74df22e53b674849e27fa4b39b792b8c


Convert richtext using .output_relative_to
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using ".output_relative_to" in the

Changelog::

- Convert richtext using .output_relative_to. Direct conversion from RichText if no longer supported as we *always* need a context for the ITransformer. [jaroel]

Pull Request:

https://github.com/plone/plone.restapi/pull/428


Upgrading to plone.restapi 1.0a17
---------------------------------

plone.restapi 1.0a17 changed the serialization of the rich-text "text" field for content objects from using 'raw' (a unicode string with the original input markup)::

  "text": {
    "content-type": "text/plain",
    "data": "Lorem ipsum",
    "encoding": "utf-8"
  },

to using 'output' (a unicode object representing the transformed output)::

  "text": {
    "content-type": "text/plain",
    "data": "<p>Lorem ipsum</p>",
    "encoding": "utf-8"
  },

Changelog::

- Change RichText field value to use 'output' instead of 'raw' to fix inline paths. This fixes #302. [erral]

Pull Request:

https://github.com/plone/plone.restapi/pull/346

