Translations
============

Since Plone 5 the product `plone.app.multilingual`_ is included in the base
Plone installation although it is not enabled by default. plone.restapi
provides a `@translations` endpoint to handle the translation information
of the content objects.

Once we have installed `plone.app.multilingual`_ and enabled more than one
language we can link two content-items of different languages to be the
translation of each other issuing a `POST` query to the `@translations`
endpoint including the `id` of the content which should be linked to. The
`id` of the content must be a full URL of the content object:


..  http:example:: curl httpie python-requests
    :request: _json/translations_post.req


.. note::
    "id" is a required field and needs to point to an existing content on the site.

The API will return a `201 Created` response if the linking was successful.


.. literalinclude:: _json/translations_post.resp
   :language: http


After linking the contents we can get the list of the translations of that
content item by issuing a ``GET`` request on the `@translations` endpoint of
that content item.:

..  http:example:: curl httpie python-requests
    :request: _json/translations_get.req

.. literalinclude:: _json/translations_get.resp
   :language: http


To unlink the content, issue a ``DELETE`` request on the `@translations`
endpoint of the content item and provide the language code you want to unlink.:


..  http:example:: curl httpie python-requests
    :request: _json/translations_delete.req

.. note::
    "language" is a required field.

.. literalinclude:: _json/translations_delete.resp
   :language: http

.. note::
    The `@translations` endpoint works also when using `Products.LinguaPlone`_
    in Plone 4.3.x


.. _`plone.app.multilingual`: https://pypi.python.org/pypi/plone.app.multilingual
.. _`Products.LinguaPlone`: https://pypi.python.org/pypi/Products.LinguaPlone.
