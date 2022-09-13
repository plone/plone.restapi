---
myst:
  html_meta:
    "description": "Plone has a working copy feature that allows the users to create a working copy of a published or live content object, and work with it until it is ready to be published without having to edit the original object."
    "property=og:description": "Plone has a working copy feature that allows the users to create a working copy of a published or live content object, and work with it until it is ready to be published without having to edit the original object."
    "property=og:title": "Working Copy"
    "keywords": "Plone, plone.restapi, REST, API, Working, Copy"
---

# Working Copy

```{note}
This feature is available only on Plone 5 or greater.
```

Plone has a *working copy* feature provided by the core package `plone.app.iterate`.
It allows the users to create a working copy of a published or live content object, and work with it until it is ready to be published without having to edit the original object.

This process has several steps in its life cycle.


## Create working copy (a.k.a., check-out)

The user initiates the process and creates a working copy by checking out the content:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workingcopy_post.req
```

…and receives the response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workingcopy_post.resp
:language: http
```


## Get the working copy

A working copy has been created and can be accessed querying the content:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workingcopy_get.req

```

…and receives the response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workingcopy_get.resp
:language: http
```

The `GET` content of any object also states the location of the working copy, if any, as `working_copy`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workingcopy_baseline_get.req

```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workingcopy_baseline_get.resp
:language: http
```

The `GET` content of any a working copy also returns the original as `working_copy_of`:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workingcopy_wc_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workingcopy_wc_get.resp
:language: http
```


## Check-in

Once the user has finished editing the working copy and wants to update the original with the changes, they would check in the working copy:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workingcopy_patch.req

```

…and receives the response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workingcopy_patch.resp
:language: http
```

The working copy is deleted afterwards as a result of this process.
The `PATCH` can also be issued in the original (baseline) object.


## Delete the working copy (cancel check-out)

If you want to cancel the check-out and delete the working copy (in both the original and
the working copy):

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/workingcopy_delete.req

```

and receives the response:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/workingcopy_delete.resp
:language: http
```

When a working copy is deleted using the normal `DELETE` action, it also deletes the relation and cancels the check-out.
That is handled by `plone.app.iterate` internals.
