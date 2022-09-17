---
myst:
  html_meta:
    "description": "plone.restapi Upgrade Guide"
    "property=og:description": "plone.restapi Upgrade Guide"
    "property=og:title": "Upgrade Guide"
    "keywords": "Plone, plone.restapi, REST, API, Upgrade, Guide"
---

# Upgrade Guide

This upgrade guide lists all breaking changes in `plone.restapi`.
It explains the steps that are needed to upgrade to the latest version.


## Upgrading to `plone.restapi` 7.x

The navigation endpoint has been refactored.
Now its behavior is consistent regarding the `items` attribute.
Now the `items` attribute is present, even if the element of the tree does not have child elements, in which case it will be an empty array.
This might affect some logins via JavaScript, specifically if the condition is checking for the existence of the `items` attribute and expects it to be `undefined`.


## Upgrading to `plone.restapi` 6.x

`plone.restapi` 6.0.0 removes the `IAPIRequest` marker interface (<https://github.com/plone/plone.restapi/pull/819>).

It also ships with a fix that prevents converting bytestring IDs to Unicode IDs when reordering on Python 2 (<https://github.com/plone/plone.restapi/issues/827>).

All versions before `plone.restapi` 6.0.0 are potentially affected by this issue.

You may be affected by this issue and should run the fix if:

- You used the `PATCH` "ordering" functionality of `plone.restapi`
- Were using Python 2 at that point
- Are seeing issues with `objectIds()` returning mixed string types

If you need to fix object IDs, you can do one of the following:

- Use the browser view `@@plone-restapi-upgrade-fix-ordering` as a Manager to fix all folderish content types in your Plone site.
- Run the helper function `ensure_child_ordering_object_ids_are_native_strings` from `plone.restapi.upgrades.ordering` for all affected objects.
  You could do this in a custom upgrade step implemented in your policy.

We expect that most content actually will not be affected.
See <https://github.com/plone/plone.restapi/issues/827> for more details.


## Upgrading to `plone.restapi` 5.x

`plone.restapi` 5.0.0 introduces the following breaking change:

- Rename `tiles` behavior and fields to `blocks` migration step. [timo, sneridagh] (#821)

The `tiles` field has been renamed to `blocks`, and the `tiles_layout` field to `blocks_layout`. This changes the response format from:

```json
{
  "@id": "http://localhost:55001/plone/my-document",
  "…",
  "tiles_layout": [
    "#title-1",
    "#description-1",
    "#image-1"
  ],
  "tiles": {
    "…"
  }
}
```

to:

```json
{
  "@id": "http://localhost:55001/plone/my-document",
  "…",
  "blocks_layout": [
    "#title-1",
    "#description-1",
    "#image-1"
  ],
  "blocks": {
    "…"
  }
}
```

This change affects the `GET`, `PATCH`, and `POST` formats.
It should only affect you if you use Volto.


## Upgrading to `plone.restapi` 4.x

`plone.restapi` 4.0.0 introduces the following breaking changes:

1.  Fields with vocabularies now return the `token` and `title` instead of the stored value.
2.  Choice and list fields return a hyperlink to a vocabulary instead of `choices`, `enum`, and `enumNames`.
3.  Serialize widget parameters into a `widgetOptions` object instead of adding them to the top level of the schema property.
4.  The vocabularies endpoint does no longer returns an `@id` for terms, the results are batched, and terms are now listed as `items` instead of `terms` to match other batched responses.


### Serialization and Deserialization of fields with vocabularies

The serialization of fields with vocabularies, such as `Choice`, now return the `token` and the `title` of the vocabulary term instead of the stored value.
This is allows displaying the term `title` without additionally querying the vocabulary.
However it is necessary to adapt existing client implementations.

The date and time control panel previously returned a number for the `first_weekday` property:

```json
{
  "@id": "http://localhost:55001/plone/@controlpanels/date-and-time",
  "data": {
      "…",
      "first_weekday": 0,
      "…"
  },
  "…",
}
```

Now it returns an object with a `token` and a `title`:

```json
{
  "@id": "http://localhost:55001/plone/@controlpanels/date-and-time",
  "data": {
      "…",
      "first_weekday": {
          "title": "Monday",
          "token": "0"
      },
      "…"
  },
  "…"
}
```

Deserialization accepts objects that contain a token, but also just the token or the value.

However, it is highly recommended to always use the token, as vocabulary terms may contain values that are not JSON serializable.


### Choice and List fields return link to vocabulary instead of the values

Choice and List fields using named vocabularies are now serialized with a `vocabulary` property, giving the URL of the `@vocabularies` endpoint for the vocabulary instead of including `choices`,
`enum`, and `enumNames` inline.

Old Response:

```json
"choices": [
    [
        "de",
        "Deutsch"
    ],
    [
        "en",
        "English"
    ]
],
"enum": [
  "de",
  "en",
],
"enumNames": [
  "Deutsch",
  "English",
]
```

New response:

```json
"vocabulary": {
    "@id": "http://localhost:55001/plone/@vocabularies/plone.app.discussion.vocabularies.CaptchaVocabulary"
},
```


### Serialize widget parameters into a `widgetOptions` object

Serialize widget parameters into a `widgetOptions` object instead of adding them to the top level of the schema property.

Old response:

```json
"vocabulary": "plone.app.vocabularies.Users"
```

New response:

```json
"widgetOptions": {
  "pattern_options": {
    "recentlyUsed": true
  },
  "vocabulary": { "@id": "http://localhost:55001/plone/@vocabularies/plone.app.vocabularies.Users" }
}
```


### Example: Vocabularies Subjects Field

The `subjects` field is now serialized as an `array` of `string` items using the `plone.app.vocabularies.Keywords` vocabulary.

Old response:

```json
"subjects": {
  "choices": ["…"],
  "enum": ["…"],
  "enumNames": ["…"]
},
"type": "string"
```

New response:

```json
"additionalItems": true,
"type": "array",
"uniqueItems": true,
"widgetOptions": {
  "vocabulary": {
    "@id": "http://localhost:55001/plone/@vocabularies/plone.app.vocabularies.Keywords"
  }
},
"items": {
  "description": "",
  "title": "",
  "type": "string"
}
```


### Example: Available Time Zones Field (vocabulary in `items`)

Old response:

```json
"available_timezones": {
  "additionalItems": true,
  "default": [],
  "description": "The timezones, which should be available for the portal. Can be set for users and events",
  "items": {
    "choices": [
      [
        "Africa/Abidjan",
        "Africa/Abidjan"
      ],
      [
        "Africa/Accra",
        "Africa/Accra"
      ],
      "…"
    ],
    "enum": [
      "…"
    ],
    "enumNames": [
      "…"
    ]
  },
  "title": "Available timezones",
  "type": "array",
  "uniqueItems": true
}
```

New response:

```json
"available_timezones": {
  "additionalItems": true,
  "default": [],
  "description": "The timezones, which should be available for the portal. Can be set for users and events",
  "items": {
    "description": "",
    "title": "",
    "type": "string",
    "vocabulary": {
      "@id": "http://localhost:8080/Plone/@vocabularies/plone.app.vocabularies.Timezones"
    }
  },
  "title": "Available timezones",
  "type": "array",
  "uniqueItems": true
},
```


### Example: Weekday Field (vocabulary in main property)

Old response:

```json
"first_weekday": {
  "choices": [
    [
      "0",
      "Monday"
    ],
    [
      "1",
      "Tuesday"
    ],
    [
      "2",
      "Wednesday"
    ],
    [
      "3",
      "Thursday"
    ],
    [
      "4",
      "Friday"
    ],
    [
      "5",
      "Saturday"
    ],
    [
      "6",
      "Sunday"
    ]
  ],
  "description": "First day in the week.",
  "enum": [
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6"
  ],
  "enumNames": [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday"
  ],
  "title": "First weekday",
  "type": "string"
},
```

New response:

```json
"first_weekday": {
  "description": "First day in the week.",
  "title": "First weekday",
  "type": "string",
  "vocabulary": {
    "@id": "http://localhost:8080/Plone/@vocabularies/plone.app.vocabularies.Weekdays"
  }
},
```


### Vocabularies Endpoint

The vocabularies endpoint no longer returns an `@id` for terms.

The results are batched, and terms are now listed as `items` instead of `terms` to match other batched responses.

Batch size is 25 by default, but can be overridden using the `b_size` parameter.

Old response:

```json
{
  "@id": "http://localhost:55001/plone/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes",
  "terms": [
    {
      "@id": "http://localhost:55001/plone/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes/Collection",
      "title": "Collection",
      "token": "Collection"
    },
    "…"
  ]
}
```

New response:

```json
{
  "@id": "http://localhost:55001/plone/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes",
  "items": [
      {
        "title": "Collection",
        "token": "Collection"
      },
      "…"
  ],
  "items_total": 12
}
```


## Upgrading to `plone.restapi` 3.x


### Image scales

Image download URLs and image scale URLs are created using the UID-based URL formats.
This allows Plone to create different URLs when the image changes, thus ensuring caches are updated.

Old Response:

```json
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
  "…"
}
```

New Response:

```json
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
  "…"
}
```


### `@sharing` endpoint

The `available_roles` property in the response to a `GET` request to the `@sharing` endpoint has changed.
Instead of a flat list of strings, it now contains a list of dicts, with the role ID and their translated title.

Old Response:

```http
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
```

New Response:

```http
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
      "…"
  ],
  "inherit": true
}
```


### Custom Content Deserializers

If you have implemented custom content deserializers, you have to handle the new `create` keyword in the `__call__` method, which determines if deserialization is performed during object creation or while updating an object.

Deserializers should only fire an `IObjectModifiedEvent` event if an object has been updated. They should not fire it when a new object has been created.

See [Dexterity content deserializer](https://github.com/plone/plone.restapi/blob/master/src/plone/restapi/deserializer/dxcontent.py) for an example.


## Upgrading to `plone.restapi` 2.x

`plone.restapi` 2.0.0 converts all datetime, DateTime and time objects to UTC before serializing.
The translations endpoint becomes "expandable", which introduces the following breaking changes.


### Translations

Previously when using the `@translations` endpoint in `plone.restapi` 1.x, the endpoint returned a `language` key with the content object's language and a `translations` key with all its translations.

Now as the endpoint is expandable, we want the endpoint to behave like the other expandable endpoints.
As top level information, we only include the name of the endpoint on the `@id` attribute and the actual translations of the content object in an attribute called `items`.

This means that now the JSON response to a `GET` request to the {ref}`translations` endpoint does not include the language of the actual content item, and the translations are now in an attribute called `items` instead of `translations`.

Old response:

```http
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
```

New response:

```http
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
```


## Upgrading to `plone.restapi` 1.0b1

In `plone.restapi` 1.0b1 the `url` attribute on the {ref}`navigation` and {ref}`breadcrumbs` endpoint was renamed to `@id` to be consistent with other links/URLs used in `plone.restapi`.

The JSON response to a `GET` request to the {ref}`breadcrumbs` endpoint changed from using the `url` attribute for `items`:

```http
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
```

…to using the `@id` for the URL of `items`:

```http
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
```

The JSON response to a `GET` request to the {ref}`navigation` endpoint changed from using the `url` attribute for `items`:

```http
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
```

to using the `@id` for the URL of `items`:

```http
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
```

The expansion mechanism is also affected by this change when {ref}`navigation` or {ref}`breadcrumbs` endpoints are expanded.

From using `url` in the breadcrumb `items`:

```json
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
    "…"
}
```

to using `@id` in the breadcrumb `items`:

```json
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
    "…"
}
```

Changelog:

- Rename `url` attribute on navigation and breadcrumb to `@id`. [timo]

Pull Request:

- <https://github.com/plone/plone.restapi/pull/459>


## Upgrading to `plone.restapi` 1.0a25

`plone.restapi` 1.0a25 introduced three breaking changes:

- Remove `@components` navigation and breadcrumbs.
  Use top level `@navigation` and `@breadcrumb` endpoints instead. [timo]
- Remove `sharing` attributes from `GET` response. [timo, jaroel]
- Convert `richtext` using `.output_relative_to`.
  Direct conversion from `RichText` is no longer supported as we *always* need a context for the `ITransformer`. [jaroel]


### Remove @components endpoint

`plone.restapi` 1.0a25 removed the `@components` endpoint which used to provide a {ref}`navigation` and a {ref}`breadcrumbs` endpoint.

Instead of using `@components/navigation`:

```
http://localhost:8080/Plone/@components/navigation
```

Use just `@navigation`:

```
http://localhost:8080/Plone/@navigation
```

Instead of using `@components/breadcrumbs`:

```
http://localhost:8080/Plone/@components/breadcrumbs
```

Use just `@breadcrumbs`:

```
http://localhost:8080/Plone/@breadcrumbs
```

Changelog:

- Remove `@components` navigation and breadcrumbs.
  Use top level `@navigation` and `@breadcrumb` endpoints instead. [timo]

Pull Request:

- <https://github.com/plone/plone.restapi/pull/425>


### Remove `sharing` attribute

The `sharing` attribute was removed from all content `GET` responses:

```json
"sharing": {
  "@id": "http://localhost:55001/plone/collection/@sharing",
  "title": "Sharing"
},
```

Use the {ref}`sharing` endpoint that can be expanded instead.

Changelog:

- Remove `sharing` attributes from `GET` response. [timo, jaroel]

Pull Request:

- <https://github.com/plone/plone.restapi/commit/1b5e9e3a74df22e53b674849e27fa4b39b792b8c>


### Convert `richtext` using `.output_relative_to`

Use `.output_relative_to` to convert `richtext`.

Changelog:

- Convert `richtext` using `.output_relative_to.`
  Direct conversion from `RichText` is no longer supported as we *always* need a context for the `ITransformer`. [jaroel]

Pull Request:

- <https://github.com/plone/plone.restapi/pull/428>


## Upgrading to `plone.restapi` 1.0a17

`plone.restapi` 1.0a17 changed the serialization of the `richtext` "text" field for content objects from using `raw` (a Unicode string with the original input markup):

```json
"text": {
  "content-type": "text/plain",
  "data": "Lorem ipsum",
  "encoding": "utf-8"
},
```

to using `output` (a Unicode object representing the transformed output):

```json
"text": {
  "content-type": "text/plain",
  "data": "<p>Lorem ipsum</p>",
  "encoding": "utf-8"
},
```

Changelog:

- Change `RichText` field value to use `output` instead of `raw` to fix inline paths.
  This fixes #302. [erral]

Pull Request:

- <https://github.com/plone/plone.restapi/pull/346>
