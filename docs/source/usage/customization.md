---
myst:
  html_meta:
    "description": "Customizing the API with the IFieldSerializer adapter."
    "property=og:description": "Customizing the API with the IFieldSerializer adapter."
    "property=og:title": "Customizing the API"
    "keywords": "Plone, plone.restapi, REST, API, Customizing, IFieldSerializer, adapter"
---

# Customizing the API


## Content serialization


### Dexterity fields

The API automatically converts all field values to JSON compatible data, whenever possible.
However, you might use fields which store data that cannot be automatically converted, or you might want to customize the representation of certain fields.

For extending or changing the serialization of certain dexterity fields, you need to register an `IFieldSerializer` adapter.

Example:

```python
from plone.customfield.interfaces import ICustomField
from plone.dexterity.interfaces import IDexterityContent
from plone.restapi.interfaces import IFieldSerializer
from plone.restapi.serializer.converters import json_compatible
from plone.restapi.serializer.dxfields import DefaultFieldSerializer
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer


@adapter(ICustomField, IDexterityContent, Interface)
@implementer(IFieldSerializer)
class CustomFieldSerializer(DefaultFieldSerializer):

    def __call__(self):
        value = self.get_value()
        if value is not None:
            # Do custom serializing here, e.g.:
            value = value.output()

        return json_compatible(value)
```

Register the adapter in ZCML:

```xml
<configure xmlns="http://namespaces.zope.org/zope">

    <adapter factory=".serializer.CustomFieldSerializer" />

</configure>
```

The `json_compatible` function recursively converts the value to JSON compatible data, when possible.
When a value cannot be converted, a `TypeError` is raised.
It is recommended to pass all values through `json_compatible` in order to validate and convert them.

For customizing a specific field instance, a named `IFieldSerializer` adapter can be registered.
The name may either be the full dotted name of the field, such as `plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation.exclude_from_nav`, or the shortname of the field, such as `exclude_from_nav`.
