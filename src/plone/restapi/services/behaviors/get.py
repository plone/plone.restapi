from plone.autoform.interfaces import IFormFieldProvider
from plone.restapi.services import Service
from plone.restapi.types.utils import get_fieldsets
from plone.restapi.typesettings.interfaces import behavior_registrations
from zope.i18n import translate


class BehaviorsGet(Service):
    """The behaviors that can be enabled on content types."""

    def reply(self):
        items = [
            self.serialize(name, registration)
            for name, registration in sorted(behavior_registrations().items())
        ]
        return {
            "@id": f"{self.context.absolute_url()}/@behaviors",
            "items": items,
            "items_total": len(items),
        }

    def serialize(self, name, registration):
        return {
            "name": name,
            "title": translate(registration.title, context=self.request),
            "description": translate(
                registration.description or "", context=self.request
            ),
            "fieldsets": self.fieldsets(registration),
        }

    def fieldsets(self, registration):
        """The fields the behavior adds to the edit form, by fieldset.

        Empty for behaviors that add no fields.
        """
        form_schema = IFormFieldProvider(registration.interface, None)
        if form_schema is None:
            return []
        fieldsets = get_fieldsets(self.context, self.request, form_schema)
        return [
            {
                "id": fieldset["id"],
                "title": fieldset["title"],
                "fields": [field.field.getName() for field in fieldset["fields"]],
            }
            for fieldset in fieldsets
            if fieldset["fields"]
        ]
