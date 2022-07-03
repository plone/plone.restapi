---
html_meta:
  "description": "Get the current state and history of an object, or workflow, by issuing a GET request for any context."
  "property=og:description": "Get the current state and history of an object, or workflow, by issuing a GET request for any context."
  "property=og:title": "Workflow"
  "keywords": "Plone, plone.restapi, REST, API, Workflow"
---

# Workflow

```{note}
Currently the workflow support is limited to executing transitions on content.
```

In Plone, content almost always has a {term}`workflow` attached.
We can get the current state and history of an object by issuing a `GET` request for any context:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workflow_get.req
```

```{literalinclude} ../../src/plone/restapi/tests/http-examples/workflow_get.resp
:language: http
```

Now if we want to change the state of the front page to publish, we would proceed by issuing a `POST` request to the given URL:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workflow_post.req
```

```{literalinclude} ../../src/plone/restapi/tests/http-examples/workflow_post.resp
:language: http
```

We can also change the state recursively for all contained items, provide a comment, and set effective and expiration dates:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workflow_post_with_body.req
```

```{literalinclude} ../../src/plone/restapi/tests/http-examples/workflow_post_with_body.resp
:language: http
```

# Specification for the fetching and updating all the workflow present is Plone

We have to create a Get request for getting all the workflow. Post request for adding a
new workflow. Patch request for updating the existing workflow and Delete request for
deleting the specific requeset.

A workflow consist of state, transition and permission related to who can change this.

## For creating a workflow we need these field

1. Id(required)
2. Title
3. Description

## For creating a sate we need these field

1. Id(required)
2. Title
3. Description
4. Possible Transitions
5. Permission field of this state


## For creating a Transition we need these field

1. Id(required)
2. Title
3. Description
4. Destination state
5. Permission
6. Display in action box( this should be just name)

Trigger wil be intiated by the user action


# API Specification

## Get

We can make a get request to `/@@workflow which will fetch a list of all workflow with

1. Id
2. title
3. description
4. @id

For fetching the data of specific workflow we should make a `/@@worflow/[@id]` endpoint
which fetches the data related to that specifc workfow and it must contains all the data.

response :-

1. id
2. title
3. description
4. @id
5. states
6. transitions

## Post

For creating a Post request we should have all the data which we are getting for the
specifc workflow and make request to `/@@workflow`.

payload :-

1. id
2. title
3. description
4. @id
5. states
6. transitions

## Patch

For updating the previous created workflow we have to make a patch request to individual
workflow `/@@workflow/[@id]` with the updated field.

## Delete

For deleting a workflow we just have to make a post request to individual workflow
`@@workflow/[@id]` with payload `Delete: true` and that workflow will be deleted.






