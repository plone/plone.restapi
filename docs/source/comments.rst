Comments
========

Plone offers users to post comments on any content object with plone.app.discussion.

Commenting can be enabled globally, for specific content types and for single content objects.

When commenting is enabled on your content object, you can retrieve a list of all existing comments, add new comments, reply to existing comments or delete a comment.

Listing Comments
----------------

You can list the existing comment on a content object by sending a GET request to the URL of the content object and appending '/@comments':

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/comments_get.req

The server will respond with a `Status 200` and a batched list of all comments:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/comments_get.resp
   :language: http

These following fields are returned:

- @id: Link to the current endpoint
- items: a list of comments for the current resource
- items_total: the total number of comments for the resource
- batching: batching information

The items attribute returns a list of comments, each comment provides the following fields:

- @id: hyperlink to the comment
- @parent: (optional) the parent comment
- author_name: the full name of the author of this comment
- author_username: the username of the author of this comment
- comment_id: the comment ID uniquely identifies the comment
- in_reply_to: the comment ID of the parent comment
- creation_date: when the comment was placed
- modification_date: when the comment was last updated
- text: contains a 'mime-type' and 'text' attribute with the text of the comment. Default mime-type is 'text/plain'.
- user_notification: boolean value to indicate if the author of the comment requested notifications on replies


Adding a Comment
----------------

To add a new comment to a content object, send a POST request to the URL of the content object and append '/@comments' to the URL. The body of the request needs to contain a JSON structure with a 'text' attribute that contains the comment text:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/comments_add_root.req

If the creation of the comment has been successful, the server will respond with a :term:`204 No Content` status and the URL of the newly created comment in the location header:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/comments_add_root.resp
   :language: http


Replying to a Comment
---------------------

To add a direct reply to an existing comment, send a POST request to the URL of the comment you want to reply to. The body of the request needs to contain a JSON structure with a 'text' attribute that contains the comment text:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/comments_add_sub.req

If the creation of the comment has been successful, the server will respond with a :term:`204 No Content` status and the URL of the newly created comment in the location header:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/comments_add_sub.resp
   :language: http


Updating a Comment
------------------

.. note:: The permission to update a comment is, by default, only granted to the creater (owner role) of the comment.

An existing comment can be updated by sending a PATCH request to the URL of the comment. The request body needs to contain a JSON structure with at least a 'text' attribute:

..  http:example:: curl httpie python-requests
    :request: ../../src/plone/restapi/tests/http-examples/comments_update.req

The server will respond with a :term:`204 No Content` response and a location header with the comment URL when the comment has been updated successfully:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/comments_update.resp
   :language: http


Deleting a Comment
------------------

An existing comment can be deleted by sending a DELETE request to the URL of the comment.

.. note:: Deleting a comment will, by default, also delete all existing replies to that comment.

..  http:example:: curl httpie python-requests
	 :request: ../../src/plone/restapi/tests/http-examples/comments_delete.req

When the comment has been deleted successfully, the server will respond with a :term:`204 No Content` response:

.. literalinclude:: ../../src/plone/restapi/tests/http-examples/comments_delete.resp
   :language: http
