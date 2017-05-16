Comments
========

The @comments endpoint exposes comments for each object. These comments are mainly identified as conversations. Each conversation can have multiple comments inside it. Parent comment of each conversation starts with id 1.
These comments are on an object so each content can have multiple conversations.


Listing comments
----------------

Listing comments of a resource

..  http:example:: curl httpie python-requests
    :request: _json/comments_get.req

.. literalinclude:: _json/comments_get.resp
   :language: http

These following fields are returned:

- @id: Link to the current endpoint
- items: a list of comments for the current resource
- items_total: total number of comments for the resource
- batching: (optional) batching information

A comment consists of the following fields:
- @id: comment ID used for deleting and updating
- @parent: (optional) the parent comment
- author_name: the authors full name
- author_username: the authors username
- comment_id: the numerical id of the comment
- in_reply_to: the numerical id of the parent comment
- creation_date: when the comment was placed
- modification_date: when the comment was last updated
- text: the comment's text and the mime-type of the text. This is normally text/plain.
- user_notification: if the author requested notifications on replies


Adding a comment
----------------

Adding a single comment to a content object

These following fields are used:
- text: The content of the comment

..  http:example:: curl httpie python-requests
    :request: _json/comments_add_root.req

.. literalinclude:: _json/comments_add_root.resp
   :language: http


Adding a reply to a comment
---------------------------

Adding a single reply to a comment to a content object

These following fields are used:

- text: The content of the reply.
- in_reply_to: The id of the comment to which the comment is placed.

..  http:example:: curl httpie python-requests
    :request: _json/comments_add_sub.req

.. literalinclude:: _json/comments_add_sub.resp
   :language: http


Updating a comment
------------------

Updating a comment will update the specific comment. It can only be done by the owners of that comment.

..  http:example:: curl httpie python-requests
    :request: _json/comments_update.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/comments_update.resp
   :language: http


Deleting a comment
------------------

Deleting a comment will remove the specific comment. The replies to this comment will also be deleted.

..  http:example:: curl httpie python-requests
	 :request: _json/comments_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/comments_delete.resp
   :language: http
