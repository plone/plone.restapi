from plone.behavior.registration import BehaviorRegistrationNotFound
from plone.behavior.registration import lookup_behavior_registration
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISchemaSerializer
from plone.restapi.serializer.schema import _check_permission
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class InheritedBehaviorExpander:

    def __init__(self, context, request):
        self.context = context
        self.request = request
        behavior_names = self.request.form.get("expand.inherit.behaviors")
        self.behavior_names = behavior_names.split(",") if behavior_names else []

    def __call__(self, expand=False):
        if not self.behavior_names:
            return {}
        url = f"{self.context.absolute_url()}/@inherit?expand.inherit.behaviors={','.join(self.behavior_names)}"
        result = {"@id": url}
        for name in self.behavior_names:
            if expand:
                try:
                    registration = lookup_behavior_registration(name=name)
                except BehaviorRegistrationNotFound:
                    continue
                schema = registration.interface
                closest = next(
                    (
                        obj
                        for obj in self.context.aq_chain
                        if registration.marker.providedBy(obj)
                        and _check_permission("View", self, obj)
                    ),
                    None,
                )
                if closest:
                    serializer = getMultiAdapter(
                        (schema, closest, self.request), ISchemaSerializer
                    )
                    data = serializer()
                    result[name] = {
                        "from": {
                            "@id": closest.absolute_url(),
                            "title": closest.title,
                        },
                        "data": data,
                    }
        return {"inherit": result}


class InheritedBehaviorGet(Service):
    def reply(self):
        expander = InheritedBehaviorExpander(self.context, self.request)
        result = expander(expand=True)
        if "inherit" in result:
            result = result["inherit"]
        return result
