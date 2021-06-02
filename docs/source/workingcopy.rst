Working Copy
============

.. note::
    This is only available on Plone 5.

Plone has the "Working copy" feature provided by the core package ``plone.app.iterate``.
It allows the users to create a working copy of a (published or live) content object and
work with it until it's ready to be published without having to edit the original object.

This process has several steps of it's life cycle:

Create working Copy (aka Check-out)
-----------------------------------

The user initiates the process and creates a "working copy" by "checking out" the content:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workingcopy_post.req

and receives the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workingcopy_post.resp
   :language: http

Get the working copy
--------------------

A working copy has been created and can be accessed querying the content:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workingcopy_get.req


and receives the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workingcopy_get.resp
   :language: http

the GET content of any object, also states the location of the working copy, if any (``working_copy``).

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workingcopy_baseline_get.req


.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workingcopy_baseline_get.resp
   :language: http

the GET content of any a working copy also returns the original (``working_copy_of``):

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workingcopy_wc_get.req

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workingcopy_wc_get.resp
   :language: http

Check-in
---------

Once the user has finished editing the working copy and wants to update the original
with the changes in there, or "check-in" the working copy.

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workingcopy_patch.req


and receives the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workingcopy_patch.resp
   :language: http


The working copy is deleted afterwards as a result of this process. The PATCH can also be issued in the original (baseline) object.

Delete the working copy (cancel check-out)
------------------------------------------

If you want to cancel the checkout and delete the working copy (in both the original and
the working copy):

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/workingcopy_delete.req


and receives the response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/workingcopy_delete.resp
   :language: http

When a working copy is deleted using the "normal" delete action, it also deletes the
relation and cancels the check-out, but that is handled by ``plone.app.iterate`` internals.
