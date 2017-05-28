TUS resumable upload
====================

Plone REST API supports the TUS Open Protocol for Resumable File Uploads.
See http://tus.io/ for more information on TUS.


The TUS '\@upload' endpoint is available on IFolderish resources, ie Folders.



Configuration and options
-------------------------

The TUS configuration and supported options can be retrieved using HTTP OPTIONS.


..  http:example:: curl httpie python-requests
    :request: _json/tusupload_options.req

.. literalinclude:: _json/tusupload_options.resp
   :language: http


Creating an upload
------------------

A POST request is used to create a new upload. The response contains a temporary upload URL to which the file must be upload.

..  http:example:: curl httpie python-requests
    :request: _json/tusupload_post.req

.. literalinclude:: _json/tusupload_post.resp
   :language: http


Upload a (partial) file
-----------------------

A PATCH request is usued to the upload URL retrieved while creating an upload.

.. literalinclude:: _json/tusupload_patch.req
   :language: http

.. literalinclude:: _json/tusupload_patch.resp
   :language: http
   

The actual content item will be created after the upload is finalized, and the final URL will be returned.

.. literalinclude:: _json/tusupload_patch_finalized.req
   :language: http

.. literalinclude:: _json/tusupload_patch_finalized.resp
   :language: http
   

Replacing an existing file
--------------------------

An existing file can be replaced by creating an upload (POST request) with the
'\@upload-replace' endpoint instead of the '\@upload' endpoint.


Current offset
--------------

A HEAD request is issued to the upload URL to get the current known offset from the server.

..  http:example:: curl httpie python-requests
    :request: _json/tusupload_head.req

.. literalinclude:: _json/tusupload_head.resp
   :language: http


CORS
----

If you have enabled CORS on your REST backend, you need to add a few headers to your CORS policy.

See http://tus.io/protocols/resumable-upload.html#headers for a definative list and discription of the headers.

This example should work as is:
    
.. code-block:: xml

  <plone:CORSPolicy
    allow_origin="http://localhost"
    allow_methods="DELETE,GET,OPTIONS,PATCH,POST,PUT"
    allow_credentials="true"
    allow_headers="Accept,Authorization,Origin,X-Requested-With,Content-Type,Upload-Length,Upload-Offset,Tus-Resumable,Upload-Metadata"
    expose_headers="Upload-Offset,Location,Upload-Length,Tus-Version,Tus-Resumable,Tus-Max-Size,Tus-Extension,Upload-Metadata"
    max_age="3600"
    />

See the plone.rest documentation for more information on CORS policies.
