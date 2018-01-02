Upgrade Guide
=============

This upgrade guide lists all breaking changes in plone.restapi.


1.0b1 (unreleased)
------------------

In plone.restapi 1.0b1 the 'url' attribute on the @navigation and @breadcrumb
endpoint was renamed to '@id' to be consistent with other links/URLs used in
plone.restapi.

Therefore the response to a GET request to the @breadcrumbs endpoint the response changed.

Old::

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

New::

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

The response to a GET request to the @navigation endpoint changed as well.

Old::

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

The expansion mechanism is also affected by this change when @navigation or @breadcrumbs endpoints are expanded.

Old::

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

New::

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

Changelog:

- Rename 'url' attribute on navigation / breadcrumb to '@id'.
  [timo]

Pull Request:

- https://github.com/plone/plone.restapi/pull/459


1.0a25 (2017-11-23)
-------------------

plone.restapi 1.0a25 removed the @components endpoint which used to provide a
'navigation' and a 'breadcrumbs' endpoint::

  http://localhost:55001/plone/front-page/@components/navigation
  http://localhost:55001/plone/front-page/@components/breadcrumbs

Changelog:

- Remove @components navigation and breadcrumbs. Use top level @navigation and
  @breadcrumb endpoints instead.
  [timo]

Pull Request:

- https://github.com/plone/plone.restapi/pull/425



- Remove "sharing" attributes from GET response.
  [timo,jaroel]

- Convert richtext using .output_relative_to. Direct conversion from RichText
  if no longer supported as we *always* need a context for the ITransformer.
  [jaroel]


1.0a17 (2017-05-31)
-------------------

Breaking Changes:

- Change RichText field value to use 'output' instead of 'raw' to fix inline
  paths. This fixes #302.
  [erral]
