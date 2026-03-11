---
myst:
  html_meta:
    "description": "Diazo themes can be managed programmatically through the @themes endpoint in a Plone site."
    "property=og:description": "Diazo themes can be managed programmatically through the @themes endpoint in a Plone site."
    "property=og:title": "Themes"
    "keywords": "Plone, plone.restapi, REST, API, Themes, Diazo"
---

# Themes

Diazo themes can be managed programmatically through the `@themes` endpoint in a Plone site.
This endpoint requires `plone.app.theming` to be installed and the `cmf.ManagePortal` permission.

It is particularly useful in containerized deployments (such as Kubernetes) where access to the Plone UI may not be available.

## Listing themes

A list of all available themes can be retrieved by sending a `GET` request to the `@themes` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/themes_get_list.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/themes_get_list.resp
:language: http
```

The following fields are returned for each theme:

- `@id`: hypermedia link to the theme resource
- `id`: the theme identifier
- `title`: the friendly name of the theme
- `description`: description of the theme
- `active`: whether this theme is currently active
- `preview`: path to the theme preview image (or `null`)
- `rules`: path to the theme rules file

## Reading a theme

A single theme can be retrieved by sending a `GET` request with the theme ID as a path parameter:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/themes_get.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/themes_get.resp
:language: http
```

## Uploading a theme

A new theme can be uploaded by sending a `POST` request with a ZIP archive as `multipart/form-data`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/themes_post.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/themes_post.resp
:language: http
```

The following form fields are accepted:

- `themeArchive` (required): the ZIP file containing the theme
- `enable` (optional): set to `true` to activate the theme immediately after upload
- `replace` (optional): set to `true` to overwrite an existing theme with the same ID

## Activating a theme

A theme can be activated by sending a `PATCH` request with `{"active": true}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/themes_patch_activate.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/themes_patch_activate.resp
:language: http
```

## Deactivating a theme

A theme can be deactivated by sending a `PATCH` request with `{"active": false}`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/themes_patch_deactivate.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/themes_patch_deactivate.resp
:language: http
```
