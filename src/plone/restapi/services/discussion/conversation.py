# -*- coding: utf-8 -*-
from plone.app.discussion.browser.comment import EditCommentForm
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.browser.comments import CommentsViewlet
from plone.app.discussion.interfaces import IConversation
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

from datetime import datetime
import plone.protect.interfaces


class CommentsGet(Service):

    def reply(self):
        conversation = IConversation(self.context)
        serializer = getMultiAdapter(
            (conversation, self.request),
            ISerializeToJson
        )
        return serializer()


@implementer(IPublishTraverse)
class CommentsAdd(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        if name:
            self.comment_id = long(name)
            request['form.widgets.in_reply_to'] = name
        return self

    def reply(self):
        # Disable CSRF protection
        if 'IDisableCSRFProtection' in dir(plone.protect.interfaces):
            alsoProvides(self.request,
                         plone.protect.interfaces.IDisableCSRFProtection)

        conversation = IConversation(self.context)
        if self.comment_id and self.comment_id not in conversation.keys():
            self.request.response.setStatus(404)
            return

        # Fake request data
        body = json_body(self.request)
        for key, value in body.items():
            self.request.form['form.widgets.' + key] = value

        form = CommentForm(self.context, self.request)
        form.update()

        action = form.actions['comment']
        data, errors = form.extractData()
        if errors:
            raise BadRequest({'errors': [err.error for err in errors]})

        form.handleComment(form=form, action=action)

        self.request.response.setStatus(204)
        if 'location' in self.request.response.headers:
            del self.request.response.headers['location']


@implementer(IPublishTraverse)
class CommentsUpdate(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        if name:
            self.comment_id = long(name)
            request['form.widgets.comment_id'] = name
        return self

    def reply(self):
        if not self.comment_id:
            raise BadRequest("Comment id is a required part of the url")

        conversation = IConversation(self.context)
        if self.comment_id not in conversation.keys():
            self.request.response.setStatus(404)
            return
        comment = conversation[self.comment_id]

        # Permission checks
        viewlet = CommentsViewlet(self.context, self.request, view=None)
        if not (viewlet.edit_comment_allowed() and viewlet.can_edit(comment)):
            raise Unauthorized()

        # Fake request data
        body = json_body(self.request)
        for key, value in body.items():
            self.request.form['form.widgets.' + key] = value

        form = EditCommentForm(comment, self.request)
        form.__parent__ = form.context.__parent__.__parent__
        form.update()

        action = form.actions['comment']
        data, errors = form.extractData()
        if errors:
            raise BadRequest({'errors': [err.error for err in errors]})

        comment.modification_date = datetime.utcnow()
        form.handleComment(form=form, action=action)

        self.request.response.setStatus(204)
        if 'location' in self.request.response.headers:
            del self.request.response.headers['location']


@implementer(IPublishTraverse)
class CommentsDelete(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        self.comment_id = long(name)
        return self

    def reply(self):
        conversation = IConversation(self.context)
        if not self.comment_id:
            raise BadRequest("Comment id is a required part of the url")

        if self.comment_id not in conversation:
            self.request.response.setStatus(404)
            return

        comment = conversation[self.comment_id]

        # Permission checks
        viewlet = CommentsViewlet(self.context, self.request, view=None)
        can_delete = viewlet.can_delete(comment)
        doc_allowed = viewlet.delete_own_comment_allowed()
        delete_own = doc_allowed and viewlet.could_delete_own(comment)
        if not (can_delete or delete_own):
            raise Unauthorized()

        del conversation[self.comment_id]
        self.request.response.setStatus(204)
