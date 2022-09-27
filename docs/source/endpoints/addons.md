---
myst:
  html_meta:
    "description": "Add-on product records can be addressed through the @addons endpoint in a Plone site."
    "property=og:description": "Add-on product records can be addressed through the @addons endpoint in a Plone site."
    "property=og:title": "Add-ons"
    "keywords": "Plone, plone.restapi, REST, API, Add-ons"
---

# Add-ons

Add-on product records can be addressed through the `@addons` endpoint in a Plone site.
In order to address a specific record, the profile ID has to be passed as a path segment, such as `/plone/@addons/plone.session`.

Reading or writing add-ons metadata requires the `cmf.ManagePortal` permission.

## Reading add-ons records

Reading a single record:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/addons_get.req
```

Example response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/addons_get.resp
:language: http
```

## Listing add-ons records

A list of all add-ons in the portal can be retrieved by sending a `GET` request to the `@addons` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/addons_get_list.req
```

Response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/addons_get_list.resp
:language: http
```

The following fields are returned:

- `@id`: hypermedia link to the control panel
- `id`: the name of the add-on package
- `title`: the friendly name of the add-on package
- `description`: description of the add-on
- `version`: the current version of the add-on
- `is_installed`: is the add-on installed?
- `has_uninstall_profile`: does the add-on have an uninstall profile?

The query string parameter `upgradeable` is available in case you want to query only the add-ons that have an upgrade step pending.

## Installing an add-on

An individual add-on can be installed by issuing a `POST` to the given URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/addons_install.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/addons_install.resp
:language: http
```

## Uninstalling an add-on

An individual add-on can be uninstalled by issuing a `POST` to the given URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/addons_uninstall.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/addons_uninstall.resp
:language: http
```

## Upgrading an add-on

An individual add-on can be upgraded by issuing a `POST` to the given URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/addons_upgrade.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/addons_upgrade.resp
:language: http
```

## Install a profile of an add-on

You can install a profile of a given add-on by issuing a `POST` to the given URL and providing the name of the profile like:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/addons_install_profile.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/addons_install_profile.resp
:language: http
```
