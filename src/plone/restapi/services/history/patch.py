# -*- coding: utf-8 -*-
from plone.restapi.deserializer import json_body
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.CMFEditions import CMFEditionsMessageFactory as _
from Products.CMFEditions.interfaces.IModifier import FileTooLargeToVersionError  # noqa
from zExceptions import BadRequest

import six


class HistoryPatch(Service):
    def reply(self):
        body = json_body(self.request)
        message = revert(self.context, body["version"])
        return json_compatible(message)


def revert(context, version):
    pr = getToolByName(context, "portal_repository")
    pr.revert(context, version)

    title = context.title_or_id()
    if not isinstance(title, six.text_type):
        title = six.text_type(title, "utf-8", "ignore")

    if pr.supportsPolicy(context, "version_on_revert"):
        try:
            commit_msg = context.translate(
                _(u"Reverted to revision ${version}", mapping={"version": version})
            )
            pr.save(obj=context, comment=commit_msg)
        except FileTooLargeToVersionError:
            error_msg = (
                "The most current revision of the file could not "
                + "be saved before reverting because the file is "
                + "too large."
            )
            raise BadRequest({"errors": error_msg})

    msg = u"{} has been reverted to revision {}.".format(title, version)
    return {"message": msg}
