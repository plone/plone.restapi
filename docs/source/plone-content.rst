Plone Content
=============

How to get all standard Plone content representations.
The syntax is given in various tools, click on 'curl', 'http-request' or 'python-requests' to see examples.

.. note::
        For folderish types, collections or search results, the results will
        be **batched** if the size of the resultset exceeds the batch size.
        See :doc:`/batching` for more details on how to work with batched
        results.


Plone Portal Root:
------------------

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone

    .. code-block:: http-request

      http GET http://localhost:8080/Plone Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/siteroot.json
   :language: json-ld

Plone Folder:
-------------

.. example-code::

    .. code-block:: curl

        curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/folder

    .. code-block:: http-request

        http GET http://localhost:8080/Plone/folder Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/folder', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/folder.json
   :language: jsonld

Plone Document:
---------------

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/document

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/document Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/document', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/document.json
   :language: jsonld

News Item:
----------

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/newsitem

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/newsitem Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/newsitem', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/newsitem.json
   :language: json-ld

Event:
------


.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/event

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/event Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/event', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/event.json
   :language: json-ld

Image:
------

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/image

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/image Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/image', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/image.json
   :language: json-ld

File:
-----

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/file

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/file Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/file', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/file.json
   :language: json-ld

Link:
-----

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/link

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/link Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/link', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/link.json
   :language: json-ld

Collection:
-----------

.. example-code::

    .. code-block:: curl

      curl -i -H "Accept: application/json" -X GET http://localhost:8080/Plone/collection

    .. code-block:: http-request

      http GET http://localhost:8080/Plone/collection Accept:application/json

    .. code-block:: python-requests

      requests.get('http://localhost:8080/Plone/collection', auth=('admin', 'admin'), headers={'Accept': 'application/json'})

.. literalinclude:: _json/collection.json
   :language: json-ld