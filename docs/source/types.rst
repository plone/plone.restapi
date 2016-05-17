Types
=====

Available content types in a Plone site can be listed and queried by accessing the ``/@types`` endpoint on portal root::

  GET /plone/@types HTTP/1.1
  Accept: application/json

The result will contain a list of all available content types::

.. literalinclude:: _json/types.json
   :language: js

The schema of a content type can be retrieved by accessing the types endpoint together with the name of the content type, e.g.::

  GET /plone/@types/Document HTTP/1.1
  Accept: application/json+schema

.. literalinclude:: _json/types_page.json
   :language: js

The content type schema uses the `JSON Schema<http://json-schema.org/>`_ format.
