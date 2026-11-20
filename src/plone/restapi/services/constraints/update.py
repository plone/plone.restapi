from plone.restapi.deserializer import json_body
from plone.restapi.services import Service
from plone.restapi.services.constraints import get_constrain_adapter
from plone.restapi.services.constraints import NAME_TO_MODE
from plone.restapi.services.constraints import serialize_constraints
from zExceptions import BadRequest
from zExceptions import Unauthorized
from zope.interface import alsoProvides

import plone.protect.interfaces


class ConstraintsPatch(Service):
    """Update addable-type constraint settings for the current context."""

    def reply(self):
        adapter = get_constrain_adapter(self.context)
        if adapter is None:
            raise BadRequest("This context does not support type constraints.")
        if not adapter.canSetConstrainTypes():
            raise Unauthorized("You are not allowed to configure type constraints.")

        data = json_body(self.request)
        if "IDisableCSRFProtection" in dir(plone.protect.interfaces):
            alsoProvides(self.request, plone.protect.interfaces.IDisableCSRFProtection)

        mode = data.get("mode")
        locally_allowed_types = data.get("locally_allowed_types")
        immediately_addable_types = data.get("immediately_addable_types")

        if mode is not None and mode not in NAME_TO_MODE:
            raise BadRequest("mode must be one of: acquire, disabled, enabled.")

        default_ids = [fti.getId() for fti in adapter.getDefaultAddableTypes()]
        locally_allowed_types = self._validate_type_ids(
            locally_allowed_types, default_ids, "locally_allowed_types"
        )
        immediately_addable_types = self._validate_type_ids(
            immediately_addable_types, default_ids, "immediately_addable_types"
        )

        if immediately_addable_types is not None:
            # Use effective allowed types (not the raw attribute) so acquire
            # mode agrees with what GET reports.
            allowed_for_subset = (
                locally_allowed_types
                if locally_allowed_types is not None
                else list(adapter.getLocallyAllowedTypes())
            )
            extra = [
                type_id
                for type_id in immediately_addable_types
                if type_id not in allowed_for_subset
            ]
            if extra:
                raise BadRequest(
                    "immediately_addable_types must be a subset of "
                    "locally_allowed_types."
                )

        # Classic UI always writes both lists together. If only the allowed
        # list is patched, drop immediately-addable types that are no longer
        # allowed so @types stays consistent.
        if locally_allowed_types is not None and immediately_addable_types is None:
            if hasattr(self.context, "immediately_addable_types"):
                current_immediately = list(self.context.immediately_addable_types)
            else:
                current_immediately = list(adapter.getImmediatelyAddableTypes())
            immediately_addable_types = [
                type_id
                for type_id in current_immediately
                if type_id in locally_allowed_types
            ]

        if mode is not None:
            adapter.setConstrainTypesMode(NAME_TO_MODE[mode])
        if locally_allowed_types is not None:
            adapter.setLocallyAllowedTypes(locally_allowed_types)
        if immediately_addable_types is not None:
            adapter.setImmediatelyAddableTypes(immediately_addable_types)

        prefer = self.request.getHeader("Prefer")
        if prefer == "return=representation":
            self.request.response.setStatus(200)
            return serialize_constraints(self.context)

        return self.reply_no_content()

    def _validate_type_ids(self, value, default_ids, field_name):
        if value is None:
            return None
        if not isinstance(value, list) or not all(
            isinstance(item, str) for item in value
        ):
            raise BadRequest(f"{field_name} must be a list of type ids.")
        invalid = [type_id for type_id in value if type_id not in default_ids]
        if invalid:
            raise BadRequest(
                f"{field_name} contains types that are not addable here: "
                f"{', '.join(invalid)}."
            )
        return value
