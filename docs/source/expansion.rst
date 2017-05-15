Expansion
=========

Expansion is a mechanism in plone.restapi to embed additional "components",
such as navigation, breadcrumbs, schema, or workflow within the main content
response. This helps the API consumers to avoid unneccesary request.

Say you want to show a document in Plone together with the breadcrumbs and a
workflow switcher. Instead of doing three individual requests, you can just
expand the breadcrumbs and the workflow "components" within the document GET
request.

The list of expandable components is listed in the "@components" attribute
in the reponse of any content GET request::

  GET /plone/front-page HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

  {
    "@id": "http://localhost:55001/plone/front-page",
    "@type": "Document",
    "@components": [
        {"@id": "http://localhost:55001/plone/front-page/@breadcrumbs"},
        {"@id": "http://localhost:55001/plone/front-page/@navigation"},
        {"@id": "http://localhost:55001/plone/front-page/@schema"},
        {"@id": "http://localhost:55001/plone/front-page/@workflow"}
    },
    "UID": "1f699ffa110e45afb1ba502f75f7ec33",
    "title": "Welcome to Plone",
    ...
  }

Request Unexpanded:

..  http:example:: curl httpie python-requests
    :request: _json/expansion.req

Response Unexpanded:

.. literalinclude:: _json/expansion.resp
   :language: http

In order to expand and embed one or more components, use the "expand" GET
parameter and provide either a single component or a comma-separated list
of the components you want to embed. Say you want to expand the "breadcrumbs"
component::

  GET /plone/front-page?expand=breadcrumbs HTTP/1.1
  Accept: application/json
  Authorization: Basic YWRtaW46c2VjcmV0

  {
    "@id": "http://localhost:55001/plone/front-page",
    "@type": "Document",
    "@components": {
      "breadcrumbs": {
        "@id": "http://localhost:55001/plone/front-page/@components/breadcrumbs",
        "items": [
          {
            "title": "Welcome to Plone",
            "url": "http://localhost:55001/plone/front-page"
          }
        ]
      },
      "navigation": "http://localhost:55001/plone/front-page/@navigation",
      "schema": "http://localhost:55001/plone/front-page/@schema",
      "workflow": {
        "history": [
          {
            "action": null,
            "actor": "test_user_1_",
            "comments": "",
            "review_state": "private",
            "time": "2016-10-21T19:00:00+00:00"
          }
        ],
        "transitions": [
          {
            "@id": "http://localhost:55001/plone/front-page/@workflow/publish",
            "title": "Publish"
          },
          {
            "@id": "http://localhost:55001/plone/front-page/@workflow/submit",
            "title": "Submit for publication"
          }
        ]
      },
    },
    "UID": "1f699ffa110e45afb1ba502f75f7ec33",
    "title": "Welcome to Plone"
  }

Request Expanded:

..  http:example:: curl httpie python-requests
    :request: _json/expansion_expanded.req

Response Expanded:

.. literalinclude:: _json/expansion_expanded.resp
   :language: http

Here is an exaxmple of a request that expands all possible expansions:

..  http:example:: curl httpie python-requests
    :request: _json/expansion_expanded_full.req

And the response:

.. literalinclude:: _json/expansion_expanded_full.resp
   :language: http
