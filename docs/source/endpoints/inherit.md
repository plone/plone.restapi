---
myst:
  html_meta:
    "description": "The inherit endpoint shows values inherited from content items higher in the hierarchy."
    "property=og:description": "The inherit endpoint shows values inherited from content items higher in the hierarchy."
    "property=og:title": "Inherit behaviors"
    "keywords": "Plone, plone.restapi, REST, API, inherit, acquisition, behaviors"
---

(inherit-behaviors-label)=

# Inherit behaviors

Plone content items are arranged in a hierarchy.
Each content item has a parent, each of which may have its own parent, continuing all the way to the Plone site root.
Together, the chain of parents are _ancestors_ of the content item.

The `@inherit` service makes it possible to access data from a behavior defined on one of these ancestors.

```{tip}
Inheriting behaviors is similar to the concept of {term}`acquisition` in Zope, but it doesn't happen automatically, so it's safer.
```

To use the service, send a `GET` request to the `@inherit` endpoint in the context of the content item that is the starting point for inheriting.
Specify the `expand.inherit.behaviors` parameter as a comma-separated list of behaviors.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/inherit_get.req
```

For each behavior, the service will find the closest ancestor which provides that behavior.
The result includes `from` (the `@id` and `title` of the item from which values were inherited) and `data` (values for any fields that are part of the behavior).

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/inherit_get.resp
:language: http
```

Ancestor items for which the current user lacks the `View` permission will be skipped.

(inherit-behaviors-expansion-label)=

## Expansion

This endpoint can be used with the {doc}`../usage/expansion` mechanism which allows getting more information about a content item in one query, avoiding unnecessary requests.

You can make a `GET` request for a content item, and include parameters to request `inherit` expansion for specific behaviors:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/inherit_expansion.req
```

The response will include data from the `@inherit` endpoint within the `@components` property:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/inherit_expansion.resp
:language: http
```
