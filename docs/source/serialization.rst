Serialization
=============

Throughout the REST API, content needs to be serialized and deserialized to and from JSON representations.

In general, the format used for serializing content when reading from the API is the same as is used to submit content to the API for writing.

Basic Types
-----------

Basic Python data types that have a corresponding type in JSON, like integers or strings, will simply be translated between the Python type and the respective JSON type.

Dates and Times
---------------

Since JSON doesn't have native support for dates/times, the Python/Zope datetime types will be serialized to an ISO 8601 datestring.

======================================= ======================================
Python                                  JSON
======================================= ======================================
``time(19, 45, 55)``                    ``'19:45:55'``
``date(2015, 11, 23)``                  ``'2015-11-23'``
``datetime(2015, 11, 23, 19, 45, 55)``  ``'2015-11-23T19:45:55'``
``DateTime('2015/11/23 19:45:55')``     ``'2015-11-23T19:45:55'``
======================================= ======================================


RichText fields
---------------

RichText fields will be serialized as follows:

A ``RichTextValue`` like

.. code-block:: python

    RichTextValue(u'<p>Hallöchen</p>',
                  mimeType='text/html',
                  outputMimeType='text/html')

will be serialized to

.. code-block:: json

    {
      "data": "<p>Hall\u00f6chen</p>",
      "content-type": "text/html",
      "encoding": "utf-8"
    }

File / Image Fields
-------------------

Download (serialization)
^^^^^^^^^^^^^^^^^^^^^^^^

For download, a file field will be serialized to a mapping that contains the
file's most basic metadata, and a hyperlink that the client can follow to
download the file:

.. code-block:: json

      {
        "...": "",
        "@type": "File",
        "title": "My file",
        "file": {
          "content-type": "application/pdf",
          "download": "http://localhost:55001/plone/file/@@download/file",
          "filename": "file.pdf",
          "size": 74429
        }
      }

That URL in the ``download`` property points to the regular Plone download
view. The client can send a ``GET`` request to that URL with an ``Accept``
header containing the MIME type indicated in the ``content-type`` property,
and will get a response containing the file.

Image fields are serialized in the same way, except that their serialization
contains their ``width`` and ``height``, and an additional property
``scales`` that contains a mapping with the available image scales:

.. code-block:: json

    {
      "icon": {
        "download": "http://localhost:55001/plone/image/@@images/image/icon",
        "height": 32,
        "width": 24
      },
      "large": {
        "download": "http://localhost:55001/plone/image/@@images/image/large",
        "height": 768,
        "width": 576
      },
      "..." : {}
    }


Upload (deserialization)
^^^^^^^^^^^^^^^^^^^^^^^^

For file or image fields, the client must provide the file's data as a mapping
containg the file data and some additional metadata:

- ``data`` - the base64 encoded contents of the file
- ``encoding`` - the encoding you used to encode the data, so usually `base64`
- ``content-type`` - the MIME type of the file
- ``filename`` - the name of the file, including extension

.. code-block:: json

      {
        "...": "",
        "@type": "File",
        "title": "My file",
        "file": {
            "data": "TG9yZW0gSXBzdW0uCg==",
            "encoding": "base64",
            "filename": "lorem.txt",
            "content-type": "text/plain"}
      }


Relations
---------

Serialization
^^^^^^^^^^^^^

A ``RelationValue`` will be serialized to a short summary representation of the referenced object:

.. code-block:: json

    {
      "@id": "http://nohost/plone/doc1",
      "@type": "DXTestDocument",
      "title": "Document 1",
      "description": "Description"
    }

The ``RelationList`` containing that reference will be represended as a list in JSON.

Deserialization
^^^^^^^^^^^^^^^

In order to set a relation when creating or updating content, you can use one
of several ways to specify relations:

======================================= ======================================
Type                                    Example
======================================= ======================================
UID                                     ``'9b6a4eadb9074dde97d86171bb332ae9'``
IntId                                   ``123456``
Path                                    ``'/plone/doc1'``
URL                                     ``'http://localhost:8080/plone/doc1'``
======================================= ======================================