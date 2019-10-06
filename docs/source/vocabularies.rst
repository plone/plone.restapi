.. _vocabularies:

Vocabularies and Sources
========================

Vocabularies are a set of allowed choices that back a particular field.
They contain so called *terms* which represent those allowed choices.
Sources are a similar, but are a more generic and dynamic concept.

Concepts
--------

**Vocabularies** contain a list of terms.
These terms are usually tokenized, meaning that in addition to a term's value, it also has a ``token`` which is a machine-friendly identifier for the term (7bit ASCII).

.. note::
    Since the underlying value of a term might not necessarily be serializable (it could be an arbitrary Python object), ``plone.restapi`` only exposes and accepts tokens, and will transparently convert between tokens and values during serialization / deseralization.
    For this reason, the following endpoints only support *tokenized* vocabularies / sources, and they do not expose the terms' values.

Terms can also have a ``title``, which is intended to be the user-facing label for the term.
For vocabularies or sources whose terms are only tokenized, but not titled, ``plone.restapi`` will fall back to using the token as the term title.

**Sources** are similar to vocabularies, but they tend to be more dynamic in nature, and are often used for larger sets of terms.
They are also not registered with a global name like vocabularies, but are instead addressed via the field they are assigned to.

**Query Sources** are sources that are capable of being queried / searched.
The source will then return only the subset of terms that match the query.

The use of such a source is usually a strong indication that no attempt should be made to enumerate the full set of terms, but instead the source should only be queried, by presenting the user with an autocomplete widget for example.

Both vocabularies and sources can be context-sensitive, meaning that they take the context into account and their contents may therefore change depending on the context they're invoked on.

This section can only provide a basic overview of vocabularies and related concepts.
For a more in-depth explanation please refer to the `Plone documentation <https://docs.plone.org/develop/plone/forms/vocabularies.html>`_.

Endpoints overview
------------------

In ``plone.restapi`` these three concepts are exposed through three separate endpoints (described in more detail below):

- **@vocabularies**/(vocab_name)
- **@sources**/(field_name)
- **@querysources**/(field_name) **?query=** (search_query)

While the ``@vocabularies`` and ``@sources`` endpoints allow to *enumerate* terms (and optionally have terms filtered server-side), the ``@querysources`` endpoint **only** allows for searching the respective source.


List all vocabularies
---------------------

.. http:get:: (context)/@vocabularies

To retrieve a list of all the available vocabularies, send a ``GET`` request to the ``@vocabularies`` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/vocabularies.req

The response will include a list with the URL (``@id``) and the names (``title``) of all the available vocabularies in Plone:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/vocabularies.resp
   :language: http


Get a vocabulary
----------------

.. http:get:: (context)/@vocabularies/(vocab_name)

To enumerate the terms of a particular vocabulary, use the ``@vocabularies`` endpoint with the name of the vocabulary, e.g. ``/plone/@vocabularies/plone.app.vocabularies.ReallyUserFriendlyTypes``.
The endpoint can be used with the site root and content objects.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/vocabularies_get.req

The server will respond with a list of terms.
The title is purely for display purposes.
The token is what should be sent to the server to address that term.

.. note::
    Vocabulary terms will be **batched** if the size of the resultset exceeds the batch size.
    See :doc:`/batching` for more details on how to work with batched results.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/vocabularies_get.resp
   :language: http

Filter Vocabularies
^^^^^^^^^^^^^^^^^^^

.. http:get:: (context)/@vocabularies/(vocab_name)?title=(filter_query)
.. http:get:: (context)/@vocabularies/(vocab_name)?token=(filter_query)

Vocabulary terms can be filtered using the ``title`` or ``token`` parameter.

Use the ``title`` paramenter to filter vocabulary terms by title.
E.g. search for all terms that contain the string ``doc`` in the title:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_title.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_title.resp
   :language: http

Use the ``token`` paramenter to filter vocabulary terms by token.
This is useful in case that you have the token and you need to retrieve the ``title``.
E.g. search the term ``doc`` in the token:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_token.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/vocabularies_get_filtered_by_token.resp
   :language: http

.. note::
    You must not filter by title and token at the same time.
    The API returns a 400 response code if you do so.


Get a source
------------

.. http:get:: (context)/@sources/(field_name)

To enumerate the terms of a field's source, use the ``@sources`` endpoint on a specific context, and pass the field name as a path parameter, e.g. ``/plone/doc/@sources/some_field``.

Because sources are inherently tied to a specific field, this endpoint can only be invoked on content objects, and the source is addressed via the field name its used for, instead of a global name (which sources don't have).

Otherwise the endpoint behaves the same as the ``@vocabularies`` endpoint.

Example:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/sources_get.req

The server will respond with a list of terms.
The title is purely for display purposes.
The token is what should be sent to the server to address that term.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/sources_get.resp
   :language: http

.. note::
    Technically there can be sources that are not iterable (ones that only implement ``ISource``, but not ``IIterableSource``).
    These cannot be enumerated using the ``@sources`` endpoint, and it will respond with a corresponding error.


Querying a query source
-----------------------

.. http:get:: (context)/@querysources/(field_name)?query=(search_query)

Query sources (sources implementing `IQuerySource`) can be queried using this endpoint, by passing the search term in the ``query`` parameter.
This search term will be passed to the query source's ``search()`` method, and the source's results are returned.

Example:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/querysources_get.req

The server will respond with a list of terms.
The title is purely for display purposes.
The token is what should be sent to the server to address that term.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/querysources_get.resp
   :language: http

.. note::
    Even though technically sources that implement ``IQuerySource`` are required to implement ``__iter__`` as well (when strictly following the interface interitance hierarchy), they usually are used in Plone in situations where their full contents shouldn't or can't be enumerated (imagine a source of all users, backed by a large LDAP, for example).

    For this reason, ``plone.restapi`` takes the stance that the ``IQuerySource`` interface is a strong indication that this source should **only** be queried, and therefore doesn't support enumeration of terms via the ``@querysources`` endpoint.

    *(If the source does actually implement IIterableSource in addition to IQuerySource, it can still be enumerated via the @sources endpoint)*
