.. _`translations`:

Translations
============

.. note::
    This is only available on Plone 5.

Since Plone 5 the product `plone.app.multilingual`_ is included in the base
Plone installation although it is not enabled by default.

Multilingualism in Plone not only allows the managers of the site to configure
the site interface texts to be in one language or another (such as the
configuration menus, error messages, information messages or other static
text) but also to configure Plone to handle multilingual content. To achieve
that it provides the user interface for managing content translations.

You can get additional information about the multilingual capabilities of Plone
in the `documentation`_.

In connection with that capabilities, plone.restapi provides a `@translations`
endpoint to handle the translation information of the content objects.

Once we have installed `plone.app.multilingual`_ and enabled more than one
language we can link two content-items of different languages to be the
translation of each other issuing a `POST` query to the `@translations`
endpoint including the `id` of the content which should be linked to. The
`id` of the content must be a full URL of the content object:


..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/translations_post.req


.. note::
    "id" is a required field and needs to point to an existing content on the site.

The API will return a `201 Created` response if the linking was successful.


.. literalinclude:: ../../src/plone/restapi/tests/http-examples/translations_post.resp
   :language: http


We can also use the object's path to link the translation instead of the full URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples//translations_post_by_id.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples//translations_post_by_id.resp
   :language: http


We can also use the object's UID to link the translation:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples//translations_post_by_uid.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples//translations_post_by_id.resp
   :language: http


After linking the contents we can get the list of the translations of that
content item by issuing a ``GET`` request on the `@translations` endpoint of
that content item.:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/translations_get.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/translations_get.resp
   :language: http


To unlink the content, issue a ``DELETE`` request on the `@translations`
endpoint of the content item and provide the language code you want to unlink.:


..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/translations_delete.req

.. note::
    "language" is a required field.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/translations_delete.resp
   :language: http

Creating a translation from an existing content
-----------------------------------------------

The POST content endpoint to a folder is capable also of linking this new content with an
exising translation using two parameters: ``translationOf`` and ``language``.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/translations_link_on_post.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/translations_link_on_post.resp
   :language: http

Get location in the tree for new translations
---------------------------------------------

When you create a translation in Plone, there are policies in place for finding a suitable
placement for it. This endpoint returns the proper placement for the newly going to be
created translation.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/translation_locator.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/translation_locator.resp
   :language: http

Expansion
---------

This endpoint can be used with the :ref:`expansion name` mechanism which allows to get additional
information about a content item in one query, avoiding unnecesary requests.

If a simple ``GET`` request is done on the content item, a new entry will be shown on the `@components`
entry with the URL of the `@translations` endpoint:



.. _`plone.app.multilingual`: https://pypi.python.org/pypi/plone.app.multilingual
.. _`Products.LinguaPlone`: https://pypi.python.org/pypi/Products.LinguaPlone.
.. _`documentation`: https://docs.plone.org/develop/plone/i18n/translating_content.html
