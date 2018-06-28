TUS resumable upload
====================

plone.restapi supports the `TUS Open Protocol <http://tus.io>`_ for resumable file uploads.
There is a `@tus-upload` endpoint to upload a file and a `@tus-replace` endpoint to replace an existing file.


Creating an Upload URL
----------------------

.. note:: POST requests to the `@tus-upload` endpoint are allowed on all IFolderish content types (e.g. Folder).

To create a new upload, send a POST request to the `@tus-upload` endpoint.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/tusupload_post.req

The server will return a temporary upload URL in the location header of the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_post.resp
   :language: http

The file can then be uploaded in the next step to that temporary URL.


Uploading a File
----------------

.. note:: PATCH requests to the `@tus-upload` endpoint are allowed on all IContentish content types.

Once a temporary upload URL has been created, a client can send a PATCH request to upload a file. The file content should be send in the body of the request:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_patch_finalized.req
   :language: http

When just a single file is uploaded at once, the server will respond with a `204: No Content` response after a successful upload.
The HTTP location header contains he URL of the newly created content object:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_patch_finalized.resp
   :language: http


Partial Upload
--------------

TUS allows partial upload of files.
A partial file is also uploaded by sending a PATCH request to the temporary URL:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_patch.req
   :language: http

The server will also respond with a `204: No content` response.
Though, instead of providing the final file URL in the 'location' header, the server provides an updated 'Upload-Offset' value, to tell the client the new offset:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_patch.resp
   :language: http

When the last partial file has been uploaded, the server will contain the final file URL in the 'location' header.


Replacing Existing Files
------------------------

TUS can also be used to replace an existing file by sending a POST request to the `@tus-replace` endpoint instead.

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusreplace_post.req
   :language: http

The server will respond with a `201: Created` status and return the URL of the temprorary created upload resource
in the location header of the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_post.resp
   :language: http

The file can then be uploaded to that URL using the PATCH method in the same way as creating a new file:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusreplace_patch.req
   :language: http

The server will respond with a `204: No Content` response and the final file URL in the HTTP location header:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusreplace_patch.resp
   :language: http


Asking for the Current File Offset
----------------------------------

To ask the server for the current file offset, the client can send a HEAD request to the upload URL:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/tusupload_head.req

The server will respond with a `200: Ok` status and the current file offset in the 'Upload-Offset' header:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_head.resp
   :language: http


Configuration and Options
-------------------------

The current TUS configuration and a list of supported options can be retrieved sending an OPTIONS request to the `@tus-upload` endpoint:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/tusupload_options.req

The server will respond with a `204: No content` status and HTTP headers containing information about the available extentions and the TUS version:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/tusupload_options.resp
   :language: http


CORS Configuration
------------------

If you use CORS and want to make it work with TUS, you have to make sure the TUS specific HTTP headers are allowed by your CORS policy.

.. code-block:: xml

  <plone:CORSPolicy
    allow_origin="http://localhost"
    allow_methods="DELETE,GET,OPTIONS,PATCH,POST,PUT"
    allow_credentials="true"
    allow_headers="Accept,Authorization,Origin,X-Requested-With,Content-Type,Upload-Length,Upload-Offset,Tus-Resumable,Upload-Metadata"
    expose_headers="Upload-Offset,Location,Upload-Length,Tus-Version,Tus-Resumable,Tus-Max-Size,Tus-Extension,Upload-Metadata"
    max_age="3600"
    />

See the plone.rest documentation for more information on how to configure CORS policies.

See http://tus.io/protocols/resumable-upload.html#headers for a list and description of the individual headers.


Temporary Upload Directory
--------------------------

During upload files are stored in a temporary directory that by default is located in the `CLIENT_HOME` directory.
If you are using a multi ZEO client setup without session stickiness you *must* configure this to a directory shared
by all ZEO clients by setting the `TUS_TMP_FILE_DIR` environment variable. E.g. ``TUS_TMP_FILE_DIR=/tmp/tus-uploads``



