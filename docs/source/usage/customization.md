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


### Dexterity content types

The API automatically provides a default serialization for all Dexterity content types.

To customize the serialization of a given content type, define a custom adapter as shown.

```{code-block} xml
:caption: configure.zcml
<adapter
    factory=".serializers.MySerializer"
    provides="plone.restapi.interfaces.ISerializeToJson"
    for="my.package.interfaces.IMyContentType
        zope.interface.Interface"
    />
```

```{code-block} python
:caption: serializers.py
from plone import api
from plone.restapi.serializer.dxcontent import SerializeToJson


class MySerializer(SerializeToJson):

    def __call__(self, version=None, include_items=True, include_expansion=True):
        # default provided by Plone
        result = super().__call__(
            version=version,
            include_items=include_items,
            include_expansion=include_expansion,
        )
        #
        # here goes your custom logic
        #
        return result
```


```{warning}
If you modify the serialization of a content type, you might need to customize its deserialization as described in the next section.
```

#### Deserialization

The reverse of serialization is deserialization.

The API provides a default deserializer.
You can customize it with an adapter as shown.

```{code-block} xml
:caption: configure.zcml
<adapter
    factory=".deserialiers.MyDeserializer"
    provides="plone.restapi.interfaces.IDeserializeFromJson"
    for="my.package.interfaces.IMyContentType
        zope.interface.Interface"
    />
```

```{code-block} python
:caption: deserializers.py
from plone import api
from plone.restapi.deserializer.dxcontent import DeserializeFromJson


class MyDeserializer(DeserializeFromJson):

    def __call__(
        self, validate_all=False, data=None, create=False, mask_validation_errors=True
    ):
        #
        # your custom logic goes here, you might want to manipulate the `data` value
        #

        # after your custom logic, you might rely on the default provided by Plone
        result = super().__call__(
            validate_all=validate_all,
            data=data,
            create=create,
            mask_validation_errors=mask_validation_errors,
        )
        return result
```

