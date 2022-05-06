from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtility
from plone.app.redirector.interfaces import IRedirectionStorage
from Products.CMFPlone.controlpanel.browser.redirects import absolutize_path
from zope.component import getMultiAdapter
from zExceptions import BadRequest
from plone.restapi import _
import plone.protect.interfaces


@implementer(IPublishTraverse)
class AliasesPost(Service):
    """Creates new aliases"""

    def __init__(self, context, request):
        super().__init__(context, request)

    def reply(self):
        data = json_body(self.request)
        storage = getUtility(IRedirectionStorage)
        aliases = data.get("aliases", [])

        if isinstance(aliases, str):
            aliases = [
                aliases,
            ]

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        failed_aliases = []
        for alias in aliases:
            if alias.startswith("/"):
                # Check navigation root
                alias = self.edit_for_navigation_root(alias)
            else:
                failed_aliases.append(alias)
                continue

            alias, err = absolutize_path(alias, is_source=True)

            if err:
                failed_aliases.append(alias)
                continue

            storage.add(
                alias,
                "/".join(self.context.getPhysicalPath()),
                manual=True,
            )

        if len(failed_aliases) > 0:
            return {
                "type": "Error",
                "message": "Couldn't add following aliases %s " % failed_aliases,
            }
        self.request.response.setStatus(201)
        return {"message": "Successfully added the aliases %s" % aliases}

    def edit_for_navigation_root(self, alias):
        # Check navigation root
        pps = getMultiAdapter((self.context, self.request), name="plone_portal_state")
        nav_url = pps.navigation_root_url()
        portal_url = pps.portal_url()
        if nav_url != portal_url:
            # We are in a navigation root different from the portal root.
            # Update the path accordingly, unless the user already did this.
            extra = nav_url[len(portal_url) :]
            if not alias.startswith(extra):
                alias = f"{extra}{alias}"
        # Finally, return the (possibly edited) redirection
        return alias


@implementer(IPublishTraverse)
class AliasesRootPost(Service):
    """Creates new aliases via controlpanel"""

    def __init__(self, context, request):
        super().__init__(context, request)

    def reply(self):
        data = json_body(self.request)
        storage = getUtility(IRedirectionStorage)
        aliases = data.get("aliases", [])

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        for alias in aliases:
            redirection = alias["path"]
            target = alias["redirect-to"]
            abs_redirection, err = absolutize_path(redirection, is_source=True)
            abs_target, target_err = absolutize_path(target, is_source=False)

            if err and target_err:
                err = f"{err} {target_err}"
            elif target_err:
                err = target_err
            else:
                if abs_redirection == abs_target:
                    err = _(
                        "Alternative urls that point to themselves will cause"
                        " an endless cycle of redirects."
                    )
            if err:
                raise BadRequest(err)

            storage.add(abs_redirection, abs_target, manual=True)

        self.request.response.setStatus(201)
        return {"message": "Successfully added the aliases %s" % aliases}
