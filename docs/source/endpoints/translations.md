---
myst:
  html_meta:
    "description": "plone.restapi provides a @translations endpoint to handle the translation information of the content objects."
    "property=og:description": "plone.restapi provides a @translations endpoint to handle the translation information of the content objects."
    "property=og:title": "Translations"
    "keywords": "Plone, plone.restapi, REST, API, Translations, plone.app.multilingual, multilingual"
---

(translations)=

# Translations

```{note}
Translations are implemented for Plone 5 or greater.
```

Since Plone 5, the product [`plone.app.multilingual`](https://pypi.org/project/plone.app.multilingual/) is included in the base Plone installation.
It is not enabled by default.

Site interface texts include the configuration menus, error messages, information messages, and other static text.
Multilingualism in Plone not only allows the managers of the site to configure the site interface texts to be in one language or another, but also to configure Plone to handle multilingual content.
To achieve that, Plone provides the user interface for managing content translations.

You can get additional information about the multilingual capabilities of Plone in the [documentation](https://5.docs.plone.org/develop/plone/i18n/translating_content.html).

In connection with those capabilities, `plone.restapi` provides a `@translations` endpoint to handle the translation information of the content objects.

Once we have installed `plone.app.multilingual` and enabled more than one language, we can link two content items of different languages to be the translation of each other issuing a `POST` query to the `@translations` endpoint, including the `id` of the content to which it should be linked.
The `id` of the content must be a full URL of the content object:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/translations_post.req
```

```{note}
`id` is a required field, and needs to point to existing content on the site.
```

The API will return a {term}`201 Created` response, if the linking was successful:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/translations_post.resp
:language: http
```

We can also use the object's path to link the translation instead of the full URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples//translations_post_by_id.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples//translations_post_by_id.resp
:language: http
```

We can also use the object's UID to link the translation:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples//translations_post_by_uid.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples//translations_post_by_id.resp
:language: http
```

After linking the contents, we can get the list of the translations of that content item by issuing a `GET` request on the `@translations` endpoint of that content item:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/translations_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/translations_get.resp
:language: http
```

To unlink the content, issue a `DELETE` request on the `@translations` endpoint of the content item, and provide the language code you want to unlink:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/translations_delete.req
```

```{note}
`language` is a required field.
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/translations_delete.resp
:language: http
```


## Creating a translation from an existing content

The `POST` content endpoint to a folder is also capable of linking this new content with an
exising translation using two parameters: `translationOf` and `language`.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/translations_link_on_post.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/translations_link_on_post.resp
:language: http
```


## Get location in the tree for new translations

When you create a translation in Plone, there are policies in place for finding a suitable placement for it.
This endpoint returns the proper placement for the newly created translation:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/translation_locator.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/translation_locator.resp
:language: http
```


## Expansion

This endpoint can be used with the {doc}`expansion` mechanism which allows getting additional information about a content item in one query, avoiding unnecessary requests.

If a simple `GET` request is done on the content item, a new entry will be shown on the `@components` entry, with the URL of the `@translations` endpoint:
