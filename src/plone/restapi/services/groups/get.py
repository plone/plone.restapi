from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.interfaces import ISerializeToJsonSummary
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


DEFAULT_SEARCH_RESULTS_LIMIT = 25


@implementer(IPublishTraverse)
class GroupsGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        self.query = self.request.form.copy()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_group_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (group id)")
        return self.params[0]

    def _get_group(self, group_id):
        portal = getSite()
        portal_groups = getToolByName(portal, "portal_groups")
        return portal_groups.getGroupById(group_id)

    def _get_groups(self):
        portal = getSite()
        portal_groups = getToolByName(portal, "portal_groups")
        return portal_groups.listGroups()

    def _get_filtered_groups(self, query, limit):
        portal = getSite()
        portal_groups = getToolByName(portal, "portal_groups")
        results = portal_groups.searchGroups(id=query, max_results=limit)
        return [portal_groups.getGroupById(group["groupid"]) for group in results]

    def reply(self):
        if len(self.query) > 0 and len(self.params) == 0:
            query = self.query.get("query", "")
            limit = self.query.get("limit", DEFAULT_SEARCH_RESULTS_LIMIT)
            if query:
                groups = self._get_filtered_groups(query, limit)
                result = []
                for group in groups:
                    serializer = queryMultiAdapter(
                        (group, self.request), ISerializeToJsonSummary
                    )
                    result.append(serializer())
                return result
            else:
                raise BadRequest("Query string supplied is not valid")

        if len(self.params) == 0:
            result = []
            for group in self._get_groups():
                serializer = queryMultiAdapter(
                    (group, self.request), ISerializeToJsonSummary
                )
                result.append(serializer())
            return result
        # we retrieve the user on the user id not the username
        group = self._get_group(self._get_group_id)
        if not group:
            self.request.response.setStatus(404)
            return
        serializer = queryMultiAdapter((group, self.request), ISerializeToJson)
        return serializer()
