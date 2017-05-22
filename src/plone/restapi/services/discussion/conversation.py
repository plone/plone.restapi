# -*- coding: utf-8 -*-
from AccessControl import getSecurityManager
from Acquisition import aq_inner
from plone.app.discussion.browser.comment import EditCommentForm
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.interfaces import IConversation
from plone.app.discussion.interfaces import IDiscussionSettings
from plone.registry.interfaces import IRegistry
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.security.interfaces import IPermission

from datetime import datetime
import plone.protect.interfaces


def permission_exists(permission_id):
    permission = queryUtility(IPermission, permission_id)
    return permission is not None


def fix_location_header(context, request):
    # This replaces the location header as sent by p.a.discussion's forms with
    # a RESTapi compatible location.
    location = request.response.headers.get('location')
    if location and '#' in location:
        comment_id = location.split('#')[-1]
        url = '{}/@comments/{}'.format(context.absolute_url(), comment_id)
        request.response.headers['location'] = url


@implementer(IPublishTraverse)
class CommentsGet(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        if name:
            self.comment_id = long(name)
        return self

    def reply(self):
        conversation = IConversation(self.context)
        if not self.comment_id:
            serializer = getMultiAdapter(
                (conversation, self.request),
                ISerializeToJson
            )
        else:
            comment = conversation[self.comment_id]
            serializer = getMultiAdapter(
                (comment, self.request),
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
        fix_location_header(self.context, self.request)


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
        if not (self.edit_comment_allowed() and self.can_edit(comment)):
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
        fix_location_header(self.context, self.request)

    def edit_comment_allowed(self):
        # Check if editing comments is allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.edit_comment_enabled

    def can_edit(self, reply):
        """Returns true if current user has the 'Edit comments'
        permission.
        """
        return getSecurityManager().checkPermission(
            'Edit comments', aq_inner(reply)
        )


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
        can_delete = self.can_delete(comment)
        doc_allowed = self.delete_own_comment_allowed()
        delete_own = doc_allowed and self.can_delete_own(comment)
        if not (can_delete or delete_own):
            raise Unauthorized()

        del conversation[self.comment_id]
        self.request.response.setStatus(204)

    # Helper functions copied from p.a.discussion's viewlet to support Plone 4

    def _has_permission(self, permission_id):
        # Older p.a.discussion versions don't support Delete comments, in
        # which case we need to check
        permission = queryUtility(IPermission, permission_id)
        return permission is not None

    def can_review(self):
        """Returns true if current user has the 'Review comments' permission.
        """
        return getSecurityManager().checkPermission('Review comments',
                                                    aq_inner(self.context))

    def can_delete(self, reply):
        """Returns true if current user has the 'Delete comments'
        permission.
        """
        if not permission_exists('plone.app.discussion.DeleteComments'):
            # Older versions of p.a.discussion do not support this yet.
            return self.can_review()

        return getSecurityManager().checkPermission(
            'Delete comments', aq_inner(reply)
        )

    def delete_own_comment_allowed(self):
        if not permission_exists('plone.app.discussion.DeleteOwnComments'):
            # Older versions of p.a.discussion do not support this yet.
            return False
        # Check if delete own comments is allowed in the registry
        registry = queryUtility(IRegistry)
        settings = registry.forInterface(IDiscussionSettings, check=False)
        return settings.delete_own_comment_enabled

    def can_delete_own(self, comment):
        """Returns true if the current user could delete the comment if it had
        no replies. This is used to prepare hidden form buttons for JS.
        """
        if not permission_exists('plone.app.discussion.DeleteOwnComments'):
            # Older versions of p.a.discussion do not support this yet.
            return False
        try:
            return comment.restrictedTraverse(
                '@@delete-own-comment').could_delete()
        except Unauthorized:
            return False
