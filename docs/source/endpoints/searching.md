---
myst:
  html_meta:
    "description": "Content in a Plone site can be searched for by invoking the /@search endpoint in any context."
    "property=og:description": "Content in a Plone site can be searched for by invoking the /@search endpoint in any context."
    "property=og:title": "Search"
    "keywords": "Plone, plone.restapi, REST, API, Search"
---

# Search

Content in a Plone site can be searched for by invoking the `/@search` endpoint in any context:

```http
GET /plone/@search HTTP/1.1
Accept: application/json
```

A search is *contextual* by default.
In other words, it is bound to a specific context—a *collection* in HTTP REST terms—and searches within that collection and any sub-collections.

A Plone site is also a collection.
We therefore have a global search by invoking the `/@search` endpoint on the site root.
We also have contextual searches by invoking that endpoint on any other context.
All searches use the same pattern.

In terms of the resulting catalog query, this means that, by default, a search will be constrained by the path to the context on which it is invoked, unless you explicitly supply your own `path` query.

Search results are represented similar to collections:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/search.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/search.resp
:language: http
```

The default representation for search results is a summary that contains only the most basic information.
In order to return specific metadata columns, see the documentation of the `metadata_fields` parameter below.

```{note}
A search invoked on a container will by default *include that container itself* as part of the search results.
This is the same behavior as displayed by [ZCatalog](https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html), which is used internally.
If you add the query string parameter `path.depth=1` to your search, you will only get the *immediate* children of the container, and the container itself won't be part of the results.
See the Plone documentation on [searching for content within a folder](https://5.docs.plone.org/develop/plone/searching_and_indexing/query.html#searching-for-content-within-a-folder)
for more details.
```

```{note}
Search results will be *batched* if the size of the resultset exceeds the batch size.
See {doc}`../usage/batching` for more details on how to work with batched results.
```

```{warning}
The `@@search` view or the Plone `LiveSearch` widget are coded in a way that the `SearchableText` parameter is expanded by including a `*` wildcard at the end.
This is done to also match the partial results of the beginning of search terms.
The `plone.restapi` `@search` endpoint will not do that for you.
You will have to add it if you want to keep this feature.
```

## Query format

Queries and query-wide options, such as `sort_on`, are submitted as query string parameters to the `/@search` request:

```http
GET /plone/@search?SearchableText=lorem HTTP/1.1
```

This is nearly identical to the way that queries are passed to the Plone `@@search` browser view, with only a few minor differences.

For general information on how to query the Plone catalog, please refer to the [Plone Documentation on Querying](https://5.docs.plone.org/develop/plone/searching_and_indexing/query.html).

### Query options

In case you want to supply query options to a query against a particular index, you will need to flatten the corresponding query dictionary and use a dotted notation to indicate nesting.

For example, to specify the `depth` query option for a path query, the original query as a Python dictionary would look like this:

```
query = {"path": {"query": "/folder1",
                  "depth": 2}}
```

This dictionary will need to be flattened in dotted notation to pass it into a query string:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/search_options.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/search_options.resp
:language: http
```

Again this is very similar to how [Record Arguments](https://zope.readthedocs.io/en/latest/zdgbook/ObjectPublishing.html#an-aggregator-in-detail-the-record-argument) are parsed by ZPublisher, except that you can omit the `:record` suffix.

### Restricting search to multiple paths

To restrict a search to multiple paths, the original query as a Python dictionary would look like this, with an optional `depth` and `sort_on`:

```
query = {"path": {"query": ("/folder", "/folder2"),
                  "depth": 2},
         "sort_on": "path"}
```

This dictionary will need to be flattened in dotted notation to pass it into a query string.
To specify multiple paths, repeat the query string parameter.
The `requests` module will automatically do this for you if you pass it a list of values for a query string parameter.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/search_multiple_paths.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/search_multiple_paths.resp
:language: http
```

### Sorting on multiple indexes

Sorting can happen on multiple indexes, as the underlying catalog supports it. To do so the query has to contain the list of indexes to be used for sorting in the `sort_on` parameter. If wanted the ordering of the sorting can also be added in the query in the `sort_order` parameter.

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/search_sort_multiple_indexes.req
```

### Data types in queries

Because HTTP query strings contain no information about data types, any query string parameter value ends up as a string in the Zope request.
This means that for value types that are not strings, these data types need to be reconstructed on the server side in `plone.restapi`.

For most index types, their query values, and query options, `plone.restapi` can handle this for you.
If you pass it `path.query=foo&path.depth=1`, it has the necessary knowledge about the `ExtendedPathIndex`'s options to turn the string `1` for the `depth` argument back into an integer before passing the query on to the catalog.

However, certain index types, such as a `FieldIndex`, may take arbitrary data types as query values.
In that case, `plone.restapi` cannot know to what data type to cast your query value.
You will need to specify it using ZPublisher type hints:

```http
GET /plone/@search?numeric_field:int=42 HTTP/1.1
Accept: application/json
```

Please refer to the [Documentation on Argument Conversion in ZPublisher](https://zope.readthedocs.io/en/latest/zdgbook/ObjectPublishing.html#argument-conversion) for details.

(retrieving-additional-metadata)=

## Retrieving additional metadata

By default, the results are represented as summaries that contain only the most basic information about the items, such as their URL and title.
If you need to retrieve additional metadata columns, you can do so by specifying the additional column names in the `metadata_fields` parameter:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/search_metadata_fields.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/search_metadata_fields.resp
:language: http
```

The metadata from those columns will then be included in the results.
To specify multiple columns, repeat the query string parameter once for every column name.
The `requests` module will automatically do this for you if you pass it a list of values for a query string parameter.

To retrieve all metadata columns that the catalog knows about, use `metadata_fields=_all`.

```{note}
There is a difference between the full set of fields contained in an object and the set of all possible metadata columns that can be specified with `metadata_fields`.
In other words, using `metadata_fields=_all` will produce objects with a set of fields that is generally smaller than the set of fields produced by `fullobjects` (see next section).
Briefly, the fields in `metadata_fields=_all` are a subset of `fullobjects`.
A consequence of this is that certain fields can not be specifed with `metadata_fields`.
Doing so will result in a TypeError `"No converter for making <...> JSON compatible."`
In [ZCatalog](https://zope.readthedocs.io/en/latest/zopebook/SearchingZCatalog.html) terms, this reflects the difference between *catalog brains* and objects that have been *woken up*.
```

## Retrieving full objects

If the data provided as metadata is not enough, you can retrieve search results as full serialized objects equivalent to what the resource `GET` request would produce.

You do so by specifying the `fullobjects` parameter:

```{eval-rst}
..  http:example:: curl httpie python-requests
    :request: ../../../src/plone/restapi/tests/http-examples/search_fullobjects.req
```

```{literalinclude} ../../../src/plone/restapi/tests/http-examples/search_fullobjects.resp
:language: http
```

```{warning}
Be aware that this might induce performance issues when retrieving a lot of resources.
Normally the search just serializes catalog brains, but with `fullobjects`, we wake up all the returned objects.
```

## Restrict search results to Plone's search settings

By default, the search endpoint does not exclude any types from its results.
To allow the search to follow Plone's search settings schema, pass the `use_site_search_settings=1` to the `@search` endpoint request.
By doing this, the search results will be filtered based on the defined types to be searched, and will be sorted according to the default sorting order.
