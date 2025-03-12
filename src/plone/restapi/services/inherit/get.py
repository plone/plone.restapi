from plone.behavior.registration import BehaviorRegistrationNotFound
from plone.behavior.registration import lookup_behavior_registration
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.interfaces import ISchemaSerializer
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
        result = {}
        for name in self.behavior_names:
            result[name] = {
                "@id": f"{self.context.absolute_url()}/@inherit?expand.inherit.behaviors={name}"
            }
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
                    ),
                    None,
                )
                if closest:
                    serializer = getMultiAdapter(
                        (schema, self.context, self.request), ISchemaSerializer
                    )
                    data = serializer()
                    result[name].update(
                        {
                            "from": {
                                "@id": closest.absolute_url(),
                                "title": closest.title,
                            },
                            "data": data,
                        }
                    )
        return result


class InheritedBehaviorGet(Service):
    def reply(self):
        expander = InheritedBehaviorExpander(self.context, self.request)
        return expander(expand=True)
