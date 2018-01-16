Upgrade Guide
=============

This upgrade guide lists all breaking changes in plone.restapi and explains the necessary steps that are needed to upgrade to the lastest version.


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

