Comments
========

The @comments endpoint exposes comments for each object. These comments are mainly identified as conversations. Each conversation can have multiple comments inside it. Parent comment of each conversation starts with id 1.
These comments are on an object so each object can have multiple conversations.


Listing conversations for a content object
------------------------------------------

Listing conversations of a resource

..  http:example::curl httpie python-requests
	:request: _json/conversation_get.req

.. literalinclude:: _json/conversaton_get.resp
   :language: http

These following fields are returned:

- @id: link to the content endpoint of this specific version.
- conversation: Array of all the conversation for this resource. Each item in array will include conversation_id, then the array of all the comments inside that conversations. Each comment will contain comment_id, comment_date, commented_by, comment_content.


Listing single conversation for a content object
------------------------------------------------

Listing single conversation of a resource

..  http:example::curl httpie python-requests
	:request: _json/conversation_single_get.req

.. literalinclude:: _json/conversation_single_get.resp
   :language: http

These following fields are returned:

- @id: Coversation Id.
- @comments: Array of all the comments for this conversation. Each element of the Array will contain comment_id, comment_date, commented_by, comment_content.


Listing single comment from a conversation for a content object
---------------------------------------------------------------

Listing single comment from a conversation for a resource

..  http:example::curl httpie python-requests
	:request: _json/conversation_comment_get.req

.. literalinclude:: _json/conversation_comment_get.resp
   :language: http

These following fields are returned:

- @id: Comment id.
- date: Date at which it is commented.
- owner: Commenter of that comment.
- comment: The actual content of that comment.
- lastUpdated: Date at which it is last updated.


Deleting the conversation for a content Object
----------------------------------------------

Deleting the conversation will remove all the comments inside that conversation. This deletion can only be done by the owner of the resource.

..  http:example::curl httpie python-requests
	:request: _json/conversation_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/conversation_delete.resp
   :language: http


Updating a comment from a conversation for a content Object
-----------------------------------------------------------

Updating a comment will update the specific comment for a conversation. It can only be done by the owners of that comment.

..  http:example::curl httpie python-requests
	:request: _json/conversation_comment_udpate.req

A successful response to a PATCH request will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/conversation_comment_udpate.resp
   :language: http


Deleting a comment from a conversation for a content Object
-----------------------------------------------------------

Deleting a comment will remove the specific comment from a conversations. The Ids of the comments below this will not be effected.

..  http:example::curl httpie python-requests
	:request: _json/conversation_comment_delete.req

A successful response will be indicated by a :term:`204 No Content` response:

.. literalinclude:: _json/conversation_comment_delete.resp
   :language: http
