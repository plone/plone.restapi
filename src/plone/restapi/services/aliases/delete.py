from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from zope.interface import alsoProvides
from zope.interface import implementer
from zope.publisher.interfaces import IPublishTraverse
from zope.component import getUtility
from plone.app.redirector.interfaces import IRedirectionStorage
from Products.CMFPlone.controlpanel.browser.redirects import absolutize_path
import plone.protect.interfaces


@implementer(IPublishTraverse)
class AliasesDelete(Service):
    """Deletes an alias from object"""

    def __init__(self, context, request):
        super().__init__(context, request)

    def reply(self):
        data = json_body(self.request)
        storage = getUtility(IRedirectionStorage)
        aliases = data.get("aliases", [])

        if isinstance(aliases, str):
            aliases = [aliases, ]

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        failed_aliases = []
        for alias in aliases:
            alias, err = absolutize_path(alias, is_source=True)

            try:
                storage.remove(alias)
            except KeyError:
                failed_aliases.append(alias)
                continue

        if len(failed_aliases) > 0:
            return {
                "type": "Error",
                "message": "The following aliases are already removed %s " % failed_aliases,
            }

        self.request.response.setStatus(201)
        return self.reply_no_content()
