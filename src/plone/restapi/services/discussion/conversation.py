from datetime import datetime
from plone.app.discussion.browser.comment import EditCommentForm
from plone.app.discussion.browser.comments import CommentForm
from plone.app.discussion.interfaces import IConversation
from plone.restapi.deserializer import json_body
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from plone.restapi.services.discussion.utils import can_delete
from plone.restapi.services.discussion.utils import can_delete_own
from plone.restapi.services.discussion.utils import can_edit
from plone.restapi.services.discussion.utils import delete_own_comment_allowed
from plone.restapi.services.discussion.utils import edit_comment_allowed
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.component import getMultiAdapter
from zope.component import queryUtility
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.security.interfaces import IPermission

import plone.protect.interfaces


def fix_location_header(context, request):
    # This replaces the location header as sent by p.a.discussion's forms with
    # a RESTapi compatible location.
    location = request.response.headers.get("location")
    if location and "#" in location:
        comment_id = location.split("#")[-1]
        url = f"{context.absolute_url()}/@comments/{comment_id}"
        request.response.headers["location"] = url


@implementer(IPublishTraverse)
class CommentsGet(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        if name:
            self.comment_id = int(name)
        return self

    def reply(self):
        conversation = IConversation(self.context)
        if not self.comment_id:
            serializer = getMultiAdapter((conversation, self.request), ISerializeToJson)
        else:
            comment = conversation[self.comment_id]
            serializer = getMultiAdapter((comment, self.request), ISerializeToJson)
        return serializer()


@implementer(IPublishTraverse)
class CommentsAdd(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        if name:
            self.comment_id = int(name)
            request["form.widgets.in_reply_to"] = name
        return self

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        conversation = IConversation(self.context)
        if self.comment_id and self.comment_id not in list(conversation):
            self.request.response.setStatus(404)
            return

        # Fake request data
        body = json_body(self.request)
        for key, value in body.items():
            self.request.form["form.widgets." + key] = value

        form = CommentForm(self.context, self.request)
        form.update()

        action = form.actions["comment"]
        data, errors = form.extractData()
        if errors:
            raise BadRequest({"errors": [err.error for err in errors]})

        form.handleComment(form=form, action=action)

        fix_location_header(self.context, self.request)
        return self.reply_no_content()


@implementer(IPublishTraverse)
class CommentsUpdate(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        if name:
            self.comment_id = int(name)
            request["form.widgets.comment_id"] = name
        return self

    def reply(self):
        if not self.comment_id:
            raise BadRequest("Comment id is a required part of the url")

        conversation = IConversation(self.context)
        if self.comment_id not in list(conversation):
            self.request.response.setStatus(404)
            return
        comment = conversation[self.comment_id]

        # Permission checks
        if not (edit_comment_allowed() and can_edit(comment)):
            raise Unauthorized()

        # Fake request data
        body = json_body(self.request)
        for key, value in body.items():
            self.request.form["form.widgets." + key] = value

        form = EditCommentForm(comment, self.request)
        form.__parent__ = form.context.__parent__.__parent__
        form.update()

        action = form.actions["comment"]
        data, errors = form.extractData()
        if errors:
            raise BadRequest({"errors": [err.error for err in errors]})

        comment.modification_date = datetime.utcnow()
        form.handleComment(form=form, action=action)

        fix_location_header(self.context, self.request)
        return self.reply_no_content()


@implementer(IPublishTraverse)
class CommentsDelete(Service):
    comment_id = None

    def publishTraverse(self, request, name):
        self.comment_id = int(name)
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
        doc_allowed = delete_own_comment_allowed()
        delete_own = doc_allowed and can_delete_own(comment)
        if not (can_delete(comment) or delete_own):
            raise Unauthorized()

        del conversation[self.comment_id]
        return self.reply_no_content()

    # Helper functions copied from p.a.discussion's viewlet to support Plone 4

    def _has_permission(self, permission_id):
        # Older p.a.discussion versions don't support Delete comments, in
        # which case we need to check
        permission = queryUtility(IPermission, permission_id)
        return permission is not None
