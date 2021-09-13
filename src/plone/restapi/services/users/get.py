from AccessControl import getSecurityManager
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.services import Service
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import normalizeString
from zExceptions import BadRequest
from zope.component import queryMultiAdapter
from zope.component.hooks import getSite
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse


DEFAULT_SEARCH_RESULTS_LIMIT = 25


@implementer(IPublishTraverse)
class UsersGet(Service):
    def __init__(self, context, request):
        super().__init__(context, request)
        self.params = []
        portal = getSite()
        self.portal_membership = getToolByName(portal, "portal_membership")
        self.acl_users = getToolByName(portal, "acl_users")
        self.query = self.request.form.copy()

    def publishTraverse(self, request, name):
        # Consume any path segments after /@users as parameters
        self.params.append(name)
        return self

    @property
    def _get_user_id(self):
        if len(self.params) != 1:
            raise Exception("Must supply exactly one parameter (user id)")
        return self.params[0]

    def _get_user(self, user_id):
        return self.portal_membership.getMemberById(user_id)

    @staticmethod
    def _sort_users(users):
        users.sort(
            key=lambda x: x is not None
            and normalizeString(x.getProperty("fullname", ""))
        )
        return users

    def _get_users(self):
        results = {user["userid"] for user in self.acl_users.searchUsers()}
        users = [self.portal_membership.getMemberById(userid) for userid in results]
        return self._sort_users(users)

    def _get_filtered_users(self, query, limit):
        results = self.acl_users.searchUsers(id=query, max_results=limit)
        users = [
            self.portal_membership.getMemberById(user["userid"]) for user in results
        ]
        return self._sort_users(users)

    def has_permission_to_query(self):
        sm = getSecurityManager()
        return sm.checkPermission("Manage portal", self.context)

    def has_permission_to_enumerate(self):
        sm = getSecurityManager()
        return sm.checkPermission("Manage portal", self.context)

    def has_permission_to_access_user_info(self):
        sm = getSecurityManager()
        return sm.checkPermission(
            "plone.restapi: Access Plone user information", self.context
        )

    def reply(self):
        if len(self.query) > 0 and len(self.params) == 0:
            query = self.query.get("query", "")
            limit = self.query.get("limit", DEFAULT_SEARCH_RESULTS_LIMIT)
            if query:
                # Someone is searching users, check if they are authorized
                if self.has_permission_to_query():
                    users = self._get_filtered_users(query, limit)
                    result = []
                    for user in users:
                        serializer = queryMultiAdapter(
                            (user, self.request), ISerializeToJson
                        )
                        result.append(serializer())
                    return result
                else:
                    self.request.response.setStatus(401)
                    return
            else:
                raise BadRequest("Query string supplied is not valid")

        if len(self.params) == 0:
            # Someone is asking for all users, check if they are authorized
            if self.has_permission_to_enumerate():
                result = []
                for user in self._get_users():
                    serializer = queryMultiAdapter(
                        (user, self.request), ISerializeToJson
                    )
                    result.append(serializer())
                return result
            else:
                self.request.response.setStatus(401)
                return

        # Some is asking one user, check if the logged in user is asking
        # their own information or if they are a Manager
        current_user_id = self.portal_membership.getAuthenticatedMember().getId()

        if self.has_permission_to_access_user_info() or (
            current_user_id and current_user_id == self._get_user_id
        ):

            # we retrieve the user on the user id not the username
            user = self._get_user(self._get_user_id)
            if not user:
                self.request.response.setStatus(404)
                return
            serializer = queryMultiAdapter((user, self.request), ISerializeToJson)
            return serializer()
        else:
            self.request.response.setStatus(401)
            return
