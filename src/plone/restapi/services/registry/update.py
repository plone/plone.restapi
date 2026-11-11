from plone.registry import field
from plone.registry.interfaces import IRegistry
from plone.restapi.services import Service
from zope.component import getUtility
from zope.interface import alsoProvides
from zope.schema.interfaces import WrongType

import json
import plone.protect.interfaces


class RegistryUpdate(Service):
    def reply(self):
        records_to_update = json.loads(self.request.get("BODY", "{}"))
        registry = getUtility(IRegistry)

        # Disable CSRF protection
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        for key, value in records_to_update.items():
            if key not in registry:
                raise NotImplementedError(
                    "This endpoint is only intended to update existing "
                    f"records! Couldn't find key {key}"
                )
            # Issue 1575: Deal with tuple values
            try:
                registry[key] = value
            except WrongType as exc:
                if isinstance(exc.field, field.Tuple) and isinstance(value, list):
                    registry[key] = tuple(value)
                else:
                    raise exc
        return self.reply_no_content()
