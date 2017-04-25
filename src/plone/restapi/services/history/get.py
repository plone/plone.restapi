# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from plone.app.layout.viewlets.content import ContentHistoryViewlet
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.services import Service
from zope.component.hooks import getSite
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse
from Products.CMFEditions import CMFEditionsMessageFactory as _
from zope.i18n import translate

# Most of this code has been copied from
# https://github.com/plone/Products.CMFEditions/blob/master/Products/CMFEditions/browser/diff.py. # noqa


class HistoryGet(Service):

    implements(IPublishTraverse)

    def __init__(self, context, request):
        super(HistoryGet, self).__init__(context, request)
        self.repo_tool = getToolByName(context, "portal_repository")
        self.params = []
        self.context
        self.request

    def publishTraverse(self, request, name):
        # Consume any path segments after /@history as parameters
        self.params.append(name)
        return self

    def getVersion(self, version):
        if version == "current":
            return self.context
        else:
            return self.repo_tool.retrieve(self.context, int(version)).object

    def versionName(self, version):
        """
        Translate the version name. This is needed to allow translation when
        `version` is the string 'current'.
        """
        return _(version)

    def versionTitle(self, version):
        version_name = self.versionName(version)

        return translate(
            _(u"version ${version}",
              mapping=dict(version=version_name)),
            context=self.request
        )

    def reply(self):
        if len(self.params) > 0:

            version1 = self.params[0]
            version2 = self.params[1]
            if not version1:
                version1 = 'current'
            if not version2:
                version2 = 'current'
            history_metadata = self.repo_tool.getHistoryMetadata(self.context)
            retrieve = history_metadata.retrieve
            getId = history_metadata.getVersionId
            history = self.history = []
            # Count backwards from most recent to least recent
            versions_backwards = xrange(
                history_metadata.getLength(countPurged=False) - 1,
                -1,
                -1
            )
            for i in versions_backwards:
                version = retrieve(i, countPurged=False)['metadata'].copy()
                version['version_id'] = getId(i, countPurged=False)
                history.append(version)
                dt = getToolByName(self.context, "portal_diff")
            self.changeset = dt.createChangeSet(
                self.getVersion(version2),
                self.getVersion(version1),
                id1=self.versionTitle(version2),
                id2=self.versionTitle(version1))
            self.changes = [change for change in self.changeset.getDiffs()
                            if not change.same]
            return json_compatible(
                [{
                    'field': change.field,
                    'getLineDiffs': change.getLineDiffs(),
                    'html_diff': change.html_diff(),
                    'id1': change.id1,
                    'id2': change.id2,
                    'inline_diff': change.inline_diff(),
                    'inlinediff_fmt': change.inlinediff_fmt,
                    'label': change.label,
                    'meta_type': change.meta_type,
                    'ndiff': change.ndiff(),
                    'newFilename': change.newFilename,
                    'newValue': change.newValue,
                    'oldFilename': change.oldFilename,
                    'oldValue': change.oldValue,
                    'same': change.same,
                    'same_fmt': change.same_fmt,
                    'schemata': change.schemata,
                    'unified_diff': change.unified_diff(),
                } for change in self.changes]
            )
        content_history_viewlet = ContentHistoryViewlet(
            self.context,
            self.request,
            None,
            None
        )
        site_url = getSite().absolute_url()
        content_history_viewlet.navigation_root_url = site_url
        content_history_viewlet.site_url = site_url
        history = content_history_viewlet.fullHistory()
        return json_compatible(history)
