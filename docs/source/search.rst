Search
======

JSON-LD lacks support for specifying the actions you can take on a resource.
Standards that address search actions are Collection+JSON, Hydra and Siren.


Collection+JSON::

  {
    "queries" :
    [
      {
        "href" : "plone/@@search",
        "rel" : "search",
        "prompt" : "Enter search string",
        "data" : [
          {"name": "search", "value" : ""},
          {"name": "sort_on", "value": ""}
          {"name": "sort_order", "value": ""},
          {"name": "portal_type", "value": ""},
        ]
      }
    ]
  }


Hydra::

  {
    "operation": {
        "@type": "SearchAction",
        "method": "GET",
        "expects": {
            "@id": "http://schema.org/Person",
            "supportedProperty": [
                {"property": "search", "range": "Text"},
                {"property": "sort_on", "range": "Text"},
                {"property": "sort_order", "range": "Text"},
                {"property": "portal_type", "range": "Text"},
            ]
        }
    }
  }


Siren::

  {
    "actions": [{
        "class": "add-friend",
        "href": "plone/@@search",
        "method": "GET",
        "fields": [
          {"name": "search", "type" : "string"},
          {"name": "sort_on", "type": "string"}
          {"name": "sort_order", "type": "string"},
          {"name": "portal_type", "type": "string"},
        ]
    }],
    "properties": {
        "size": "2"
    },
  }
