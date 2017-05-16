Comments
========

The @comments endpoint exposes comments for each object. These comments are mainly identified as conversations. Each conversation can have multiple comments inside it. Parent comment of each conversation starts with id 1.
These comments are on an object so each content can have multiple conversations.


Listing comments
----------------

Listing comments of a resource

..  http:example::curl httpie python-requests
	:request: _json/comments_get.req

.. literalinclude:: _json/comments_get.resp
   :language: http

These following fields are returned:

- @id: link to the conversation
- comments: This subobject contains:
  - @id: link to the comments endpoint
  - items_total: total amount of items
  - batching: An optional subobject containing batching links if applicable.


Adding a comment
----------------

Adding a single comment to a content object

These following fields are used:
- text: The content of the comment

..  http:example::curl httpie python-requests
  :request: _json/comments_add_root.req

.. literalinclude:: _json/comments_add_root.resp
   :language: http


Adding a reply to a comment
---------------------------

Adding a single reply to a comment to a content object

These following fields are used:

- text: The content of the reply.
- in_reply_to: The id of the comment to which the comment is placed.

..  http:example::curl httpie python-requests
  :request: _json/comments_add_sub.req

.. literalinclude:: _json/comments_add_sub.resp
   :language: http


Updating a comment
------------------

Updating a comment will update the specific comment. It can only be done by the owners of that comment.

..  http:example::curl httpie python-requests
  :request: _json/comments_update.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/comments_update.resp
   :language: http


Deleting a comment
------------------

Deleting a comment will remove the specific comment. The replies to this comment will also be deleted.

..  http:example::curl httpie python-requests
	:request: _json/comments_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/comments_delete.resp
   :language: http
