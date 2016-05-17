Types
=====

Available content types in a Plone site can be listed and queried by accessing the ``/@types`` endpoint on portal root:

.. literalinclude:: _json/types.json
   :language: js

To get the schema of a content type by accessing the types endpoint together with the name of the content type, e.g.:

.. literalinclude:: _json/types_document.json
   :language: js

The content type schema uses the `JSON Schema <http://json-schema.org/>`_ format.
