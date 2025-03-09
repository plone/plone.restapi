from DateTime import DateTime
from DateTime.interfaces import DateTimeError
from plone.app.redirector.interfaces import IRedirectionStorage
from plone.restapi import _
from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from Products.CMFPlone.controlpanel.browser.redirects import absolutize_path
from Products.CMFPlone.controlpanel.browser.redirects import RedirectsControlPanel
from Products.statusmessages.interfaces import IStatusMessage
from zExceptions import BadRequest
from zope.component import getMultiAdapter
from zope.component import getUtility
from zope.component.hooks import getSite
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse

import logging
import plone.protect.interfaces


logger = logging.getLogger(__name__)


@implementer(IPublishTraverse)
class AliasesPost(Service):
    """Creates new aliases"""

    def reply(self):
        data = json_body(self.request)
        storage = getUtility(IRedirectionStorage)
        aliases = data.get("items", [])

        if isinstance(aliases, str):
            aliases = [
                aliases,
            ]

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        failed_aliases = []
        for alias in aliases:
            if isinstance(alias, dict):
                alias = alias.get("path")

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
                "type": "error",
                "failed": failed_aliases,
            }

        return self.reply_no_content()

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

    def _reply_csv(self):
        form = self.request.form
        if not form.get("file"):
            raise BadRequest("No file uploaded")

        file = form["file"]

        if file.headers.get("Content-Type") not in ("text/csv", "application/csv"):
            raise BadRequest("Uploaded file is not a valid CSV file")

        controlpanel = RedirectsControlPanel(self.context, self.request)
        csv_errors = controlpanel.csv_errors = []
        storage = getUtility(IRedirectionStorage)
        status = IStatusMessage(self.request)
        portal = getSite()
        controlpanel.upload(file, portal, storage, status)
        file.close()

        if csv_errors:
            self.request.response.setHeader("Content-Type", "application/json")
            self.request.response.setStatus(BadRequest)
            return {
                "type": "BadRequest",
                "message": f"Found {len(csv_errors)} errors in CSV file.",
                # Skip first item which is a notice about the delimiter
                "csv_errors": csv_errors[1:],
            }
        if err := status.show():
            if err[0].type == "error":
                raise BadRequest(err[0].message)
            elif err[0].type == "info":
                logger.info(err[0].message)
        return self.reply_no_content()

    def reply(self):
        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)
        if "multipart/form-data" in self.request.getHeader("Content-Type"):
            return self._reply_csv()

        storage = getUtility(IRedirectionStorage)
        data = json_body(self.request)
        aliases = data.get("items", [])
        for alias in aliases:
            redirection = alias.get("path")
            target = alias.get("redirect-to")
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

            date = alias.get("datetime", None)
            if date:
                try:
                    date = DateTime(date)
                except DateTimeError:
                    logger.warning("Failed to parse as DateTime: %s", date)
                    date = None

            storage.add(abs_redirection, abs_target, now=date, manual=True)

        return self.reply_no_content()
