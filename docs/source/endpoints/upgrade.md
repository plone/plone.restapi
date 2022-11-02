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

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "@id": "http://localhost:55001/plone/@upgrade",
  "upgrade_steps": {
    "6006-6007": [
      {
        "id": "cb3b910894ab80c94b6367b39bc93039",
        "title": "Run to6007 upgrade profile."
      },
      {
        "id": "bb72e6a5b0c9c6131b1efad155868131",
        "title": "Add a timezone property to portal memberdata if it is missing."
      },
      {
        "id": "62ef4eea9b3bfbd472cf349277de749b",
        "title": "Fix the portal action icons."
      },
      {
        "id": "bac1428c12e294517042a1cee5cfabdc",
        "title": "Rename the behavior collective.dexteritytextindexer to plone.textindexer"
      }
    ],
    "6007-6008": [
      {
        "id": "e5cad1e9fd65e8bd1b23519d49417e51",
        "title": "Update plonetheme.barceloneta registry"
      }
    ]
  },
  "versions": {
    "fs": "6008",
    "instance": "6006"
  }
}
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

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "@id": "http://localhost:55001/plone/@upgrade",
  "dry_run": true,
  "report": "Dry run selected.\nStarting the migration from version: 6006\nRole / permission map imported.\nActions tool imported.\nRan upgrade step: Run to6007 upgrade profile.\nRan upgrade step: Add a timezone property to portal memberdata if it is missing.\nRan upgrade step: Fix the portal action icons.\nRan upgrade step: Rename the behavior collective.dexteritytextindexer to plone.textindexer\nRan upgrade step: Update plonetheme.barceloneta registry\nEnd of upgrade path, main migration has finished.\nStarting upgrade of core addons.\nControl panel imported.\nDone upgrading core addons.\nYour Plone instance is now up-to-date.\nDry run selected, transaction aborted\n",
  "upgraded": false,
  "versions": {
    "fs": "6008",
    "instance": "6006"
  }
}
```

## Run upgrade

Send a `POST` request to the `@upgrade` endpoint, with `dry_run` set to `false`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/upgrade_post.req
```
The response will contain the result of the upgrade operation:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "@id": "http://localhost:55001/plone/@upgrade",
  "dry_run": false,
  "report": "Starting the migration from version: 6006\nRole / permission map imported.\nActions tool imported.\nRan upgrade step: Run to6007 upgrade profile.\nRan upgrade step: Add a timezone property to portal memberdata if it is missing.\nRan upgrade step: Fix the portal action icons.\nRan upgrade step: Rename the behavior collective.dexteritytextindexer to plone.textindexer\nRan upgrade step: Update plonetheme.barceloneta registry\nEnd of upgrade path, main migration has finished.\nStarting upgrade of core addons.\nControl panel imported.\nDone upgrading core addons.\nYour Plone instance is now up-to-date.\n",
  "upgraded": true,
  "versions": {
    "fs": "6008",
    "instance": "6008"
  }
}
```
