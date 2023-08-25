---
myst:
  html_meta:
    "description": "The @upgrade endpoint exposes upgrade information about the Plone backend, and supports running the upgrade of the site."
    "property=og:description": "The @upgrade endpoint exposes upgrade information about the Plone backend, and supports running the upgrade of the site."
    "property=og:title": "Upgrade"
    "keywords": "Plone, plone.restapi, REST, API, Upgrade"
---

(upgrade)=

# Upgrade

A Plone site needs to be in sync with the version available on the file system.
The `@upgrade` endpoint exposes upgrade information about the Plone backend, and supports running the upgrade of the site.

```{note}
The upgrade endpoint is protected by the `cmf.ManagePortal` permission that requires the Manager role.
```

## Get upgrade information

Send a `GET` request to the `@upgrade` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/upgrade_get.req
```

The response will contain information about available upgrade steps:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/upgrade_get.resp
:language: http
```

`fs` shows the current version of the `CMFPlone:default` profile on the filesystem.
`instance` shows the current version of the `CMFPlone:default` profile in the database.

## Dry run the upgrade

Send a `POST` request to the `@upgrade` endpoint passing the value of `dry_run` as `true`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/upgrade_post_dry_run.req
```

A dry run runs the entire upgrade, but does not commit the result to the database.
The response will contain the result of the upgrade operation, indicating `dry_run` was selected:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/upgrade_post_dry_run.resp
:language: http
```

## Run upgrade

Send a `POST` request to the `@upgrade` endpoint, with `dry_run` set to `false`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/upgrade_post.req
```

The response will contain the result of the upgrade operation:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/upgrade_post.resp
:language: http
```
