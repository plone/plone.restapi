---
myst:
  html_meta:
    "description": "The @transactions endpoint exposes transactions that have been made through the Plone website."
    "property=og:description": "The @transactions endpoint exposes transactions that have been made through the Plone website."
    "property=og:title": "Transactions"
    "keywords": "Plone, plone.restapi, REST, API, Transactions"
---

# Transactions

The `@transactions` endpoint exposes transactions that have been made through the Plone website.
Each change through the Plone website is listed.
It also allows to revert transactions so that the Plone website can be reverted to a previous state.


## Listing the Transactions of a Content Object

Listing versions and transactions of a resource:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/transactions_get.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/transactions_get.resp
:language: http
```

The following fields are returned:

`username`
: The person who made the transactions through the website.

`time`
: The time when the transaction was made through the website.

`description`
: The description of the transaction with the `path` where the transaction was made in the website.

`id`
: The transaction ID.

`size`
: The size of the transaction in bytes.


## Reverting a Transaction or a group of Transactions

Reverting a single transaction or a group of transactions can be done by sending a `PATCH` request to the `@transactions` endpoint with a list of transaction IDs you want to revert:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/transactions_revert.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/transactions_revert.resp
:language: http
```
