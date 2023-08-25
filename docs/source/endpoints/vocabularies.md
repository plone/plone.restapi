---
myst:
  html_meta:
    "description": "Vocabularies are a set of allowed choices that back a particular field, whereas sources are similar but usually too large to be enumerated and should be queried such as through an autocomplete."
    "property=og:description": "Vocabularies are a set of allowed choices that back a particular field, whereas sources are similar but usually too large to be enumerated and should be queried such as through an autocomplete."
    "property=og:title": "Vocabularies and Sources"
    "keywords": "Plone, plone.restapi, REST, API, Vocabularies, Sources"
---

(vocabularies)=

# Vocabularies and Sources

Vocabularies are a set of allowed choices that back a particular field.
They contain so-called *terms* which represent those allowed choices.
Sources are similar, but are a more generic and dynamic concept.


## Concepts

*Vocabularies* contain a list of terms.
These terms are usually tokenized, meaning that in addition to a term's value, it also has a `token`, which is a machine-friendly identifier for the term in 7-bit ASCII.

```{note}
Since the underlying value of a term might not necessarily be serializable (it could be an arbitrary Python object), `plone.restapi` only exposes and accepts tokens.
It will transparently convert between tokens and values during serialization and deseralization.
For this reason, the following endpoints only support *tokenized* vocabularies and sources, and they do not expose the terms' values.
```

Terms can also have a `title`, which is intended to be the user-facing label for the term.
For vocabularies or sources whose terms are only tokenized but not titled, `plone.restapi` will fall back to using the token as the term title.

*Sources* are similar to vocabularies, but they tend to be more dynamic in nature, and are often used for larger sets of terms.
They are also not registered with a global name like vocabularies, but are instead addressed via the field they are assigned to.

*Query Sources* are sources that are capable of being queried or searched.
The source will then return only the subset of terms that match the query.

The use of such a source is usually a strong indication that no attempt should be made to enumerate the full set of terms.
Instead, the source should only be queried, for example, by presenting the user with an autocomplete widget.

Both vocabularies and sources can be context-sensitive.
This means that they take the context into account and their contents may therefore change depending on the context in which they are invoked.

This section can only provide a basic overview of vocabularies and related concepts.
For a more in-depth explanation please refer to the [Plone documentation](https://5.docs.plone.org/develop/plone/forms/vocabularies.html).


## Endpoints overview

In `plone.restapi` these three concepts are exposed through three separate endpoints, described in more detail below:

- **`@vocabularies`**`/<vocab_name>`
- **`@sources`**`/<field_name>`
- **`@querysources`**`/<field_name>`**`?query=`**`<search_query>`

While the `@vocabularies` and `@sources` endpoints allow *enumeration* of terms and optionally filter terms server-side, the `@querysources` endpoint *only* allows for searching the respective source.


## List all vocabularies

```{eval-rst}
.. http:get:: (context)/@vocabularies
```

To retrieve a list of all the available vocabularies, send a `GET` request to the `@vocabularies` endpoint:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/vocabularies.req
```

The response will include a list with the URL (`@id`) and the names (`title`) of all the available vocabularies in Plone:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/vocabularies.resp
:language: http
```


## Get a vocabulary

```{eval-rst}
.. http:get:: (context)/@vocabularies/(vocab_name)
```

To enumerate the terms of a particular vocabulary, use the `@vocabularies` endpoint with the name of the vocabulary, for example `/plone/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes`.
The endpoint can be used with the site root and content objects:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/vocabularies_get.req
```

The server will respond with a list of terms.
The title is purely for display purposes.
The token is what should be sent to the server to address that term.

```{note}
Vocabulary terms will be *batched* if the size of the resultset exceeds the batch size.
See {doc}`../usage/batching` for more details on how to work with batched results.
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/vocabularies_get.resp
:language: http
```

By default, the vocabularies are batched.
However, you can pass the parameter `b_size=-1` to force the endpoint to return all the terms, instead of a batched response.


### Filter Vocabularies

```{eval-rst}
.. http:get:: (context)/@vocabularies/(vocab_name)?title=(filter_query)
```

```{eval-rst}
.. http:get:: (context)/@vocabularies/(vocab_name)?token=(filter_query)
```

```{eval-rst}
.. http:get:: (context)/@vocabularies/(vocab_name)?tokens=(filter_term1)&tokens=(filter_term2)&...
```

Vocabulary terms can be filtered using the `title`, `token`, or `tokens` (array) parameter.

Use the `title` parameter to filter vocabulary terms by title.
For example, search for all terms that contain the string `doc` in the title:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_title.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_title.resp
:language: http
```

Use the `token` parameter to filter vocabulary terms by token.
This is useful when you have the `token`, and you need to retrieve the `title`.
For example, search for the term `doc` in the token:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_token.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_token.resp
:language: http
```

```{note}
You must not filter by `title` and `token` at the same time.
The API returns a 400 response code if you do so.
```

Use the `tokens` parameter to filter vocabulary terms by a list of tokens:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_token_list.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_token_list.resp
:language: http
```


## Get a source

```{eval-rst}
.. http:get:: (context)/@sources/(field_name)
```

To enumerate the terms of a field's source, use the `@sources` endpoint on a specific context, and pass the field name as a path parameter, for example, `/plone/doc/@sources/some_field`.

Because sources are inherently tied to a specific field, this endpoint can only be invoked on content objects.
The source is addressed via the field name for which it is used, instead of a global name (which sources do not have).

Otherwise, the endpoint behaves the same as the `@vocabularies` endpoint.

Example:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/sources_get.req
```

The server will respond with a list of terms.
The title is purely for display purposes.
The token is what should be sent to the server to address that term:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/sources_get.resp
:language: http
```

```{note}
Technically there can be sources that are not iterable: ones that only implement `ISource`, but not `IIterableSource`.
These cannot be enumerated using the `@sources` endpoint.
It will respond with a corresponding error.
```


## Querying a query source

```{eval-rst}
.. http:get:: (context)/@querysources/(field_name)?query=(search_query)
```

Query sources—sources that implement `IQuerySource`—can be queried using this endpoint, by passing the search term in the `query` parameter.
This search term will be passed to the query source's `search()` method.
The source's results are returned.

Example:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/querysources_get.req
```

The server will respond with a list of terms.
The title is purely for display purposes.
The token is what should be sent to the server to address that term:

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/querysources_get.resp
:language: http
```

```{note}
Technically, even though sources that implement `IQuerySource` are required to implement `__iter__` as well when strictly following the interface interitance hierarchy, they usually are used in Plone in situations where their full contents should not or cannot be enumerated.
For example, imagine a source of all users, backed by a large LDAP.

For this reason, `plone.restapi` takes the stance that the `IQuerySource` interface is a strong indication that this source should *only* be queried, and therefore does not support enumeration of terms via the `@querysources` endpoint.

If the source does actually implement `IIterableSource` in addition to `IQuerySource`, it can still be enumerated via the `@sources` endpoint.
```
