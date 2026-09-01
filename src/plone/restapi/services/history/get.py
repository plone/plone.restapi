from Acquisition import aq_inner
from datetime import datetime as dt
from datetime import timezone
from plone.memoize.instance import memoize
from plone.restapi.bbb import safe_text
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from Products.CMFCore.utils import _checkPermission
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.WorkflowCore import WorkflowException
from Products.CMFEditions.Permissions import AccessPreviousVersions
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.i18nmessageid import MessageFactory
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging

_ = MessageFactory("plone")
logger = logging.getLogger(__file__)


class ContentHistory:

    def __init__(self, context, request, site_url):
        self.context = context
        self.request = request
        self.site_url = site_url

    @memoize
    def getUserInfo(self, userid):
        actor = dict(fullname=userid)
        mt = getToolByName(self.context, "portal_membership")
        info = mt.getMemberInfo(userid)
        if info is None:
            return dict(actor=actor)

        fullname = info.get("fullname", None)
        if fullname:
            actor["fullname"] = fullname

        return dict(actor=actor)

    def workflowHistory(self, complete=True):
        """Return workflow history of this context.

        Taken from plone_scripts/getWorkflowHistory.py
        """
        context = aq_inner(self.context)
        # check if the current user has the proper permissions
        if not (
            _checkPermission("Request review", context)
            or _checkPermission("Review portal content", context)
        ):
            return []

        workflow = getToolByName(context, "portal_workflow")
        review_history = []

        try:
            # Get total history.
            # Note: expected variables like 'action' may not exist:
            # the workflow may have started out without variables.
            review_history = workflow.getInfoFor(context, "review_history")

            if not complete:
                # filter out automatic transitions.
                review_history = [r for r in review_history if r.get("action")]
            else:
                review_history = list(review_history)

            portal_type = context.portal_type
            anon = _("label_anonymous_user", default="Anonymous User")
            for r in review_history:
                r["type"] = "workflow"

                # Get transition title.
                transition_title = ""
                action = r.get("action")
                if action:
                    transition_title = workflow.getTitleForTransitionOnType(
                        action, portal_type
                    )
                if not transition_title:
                    transition_title = _("Create")
                r["transition_title"] = transition_title

                # Get state title.
                r["state_title"] = workflow.getTitleForStateOnType(
                    r.get("review_state", ""), portal_type
                )

                # Get actor.
                actorid = r.get("actor")
                r["actorid"] = actorid
                if actorid is None:
                    # action performed by an anonymous user, or unknown
                    r["actor"] = {"username": anon, "fullname": anon}
                else:
                    r.update(self.getUserInfo(actorid))
            review_history.reverse()

        except WorkflowException:
            logger.debug(
                "plone.app.layout.viewlets.content: %s has no associated workflow",
                context.absolute_url(),
            )

        return review_history

    def revisionHistory(self):
        context = aq_inner(self.context)
        if not _checkPermission(AccessPreviousVersions, context):
            return []

        rt = getToolByName(context, "portal_repository", None)
        if rt is None or not rt.isVersionable(context):
            return []

        history = rt.getHistoryMetadata(context)
        may_revert = _checkPermission(
            "CMFEditions: Revert to previous versions", context
        )

        def morphVersionDataToHistoryFormat(vdata, version_id):
            meta = vdata["metadata"]["sys_metadata"]
            userid = meta["principal"]
            info = dict(
                type="versioning",
                action=_("Edited"),
                transition_title=_("Edited"),
                actorid=userid,
                time=meta["timestamp"],
                comments=meta["comment"],
                may_revert=bool(may_revert),
                version_id=version_id,
            )
            info.update(self.getUserInfo(userid))
            return info

        # History may be an empty list
        if not history:
            return history

        version_history = []
        retrieve = history.retrieve
        getId = history.getVersionId
        # Count backwards from most recent to least recent
        for i in range(history.getLength(countPurged=False) - 1, -1, -1):
            version_history.append(
                morphVersionDataToHistoryFormat(
                    retrieve(i, countPurged=False), getId(i, countPurged=False)
                )
            )

        return version_history

    def fullHistory(self):
        history = self.workflowHistory() + self.revisionHistory()
        if len(history) == 0:
            return None
        history.sort(key=lambda x: x.get("time", 0.0), reverse=True)
        return history


@implementer(IPublishTraverse)
class HistoryGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.version = None

    def publishTraverse(self, request, name):
        self.version = name
        return self

    def reply(self):
        # Traverse to historical version
        if self.version:
            serializer = queryMultiAdapter(
                (self.context, self.request), ISerializeToJson
            )
            data = serializer(version=self.version)
            return data

        # Listing historical data
        site_url = getSite().absolute_url()
        content_history = ContentHistory(self.context, self.request, site_url)
        history = content_history.fullHistory()
        if history is None:
            history = []

        for item in history:
            item["actor"] = {
                "@id": "{}/@users/{}".format(site_url, item["actorid"]),
                "id": item.pop("actorid"),
                "fullname": item["actor"].get("fullname"),
                "username": item["actor"].get("username"),
            }

            if item["type"] == "versioning":
                item["version"] = item.pop("version_id")
                item["@id"] = "{}/@history/{}".format(
                    self.context.absolute_url(), item["version"]
                )

            # Versioning entries use a timestamp,
            # workflow ISO formatted string
            if not isinstance(item["time"], str):
                item["time"] = dt.fromtimestamp(
                    int(item["time"]), tz=timezone.utc
                ).isoformat(timespec="seconds")

            # The create event has an empty 'action', but we like it to say
            # 'Create', alike the transition_title
            if item["action"] is None:
                item["action"] = "Create"

            # We want action, state and transition names translated
            if "state_title" in item:
                item["state_title"] = self.context.translate(
                    safe_text(item["state_title"]), context=self.request
                )

            if "transition_title" in item:
                item["transition_title"] = self.context.translate(
                    safe_text(item["transition_title"]), context=self.request
                )

            if "action" in item:
                item["action"] = self.context.translate(
                    safe_text(item["action"]), context=self.request
                )

        return json_compatible(history)
