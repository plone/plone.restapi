
=====================
 Customizing the API
=====================

Content serialization
=====================

Dexterity fields
----------------

The API automatically converts all field values to JSON compatible
data, whenever possible.
However, you might use fields which store data that cannot be automatically
converted, or you might want to customize the representation of certain
fields.

For extending or changing the serializing of certain dexterity fields you
need to register an ``IFieldSerializer``-adapter.

Example:

.. code:: python

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


Register the adapter in ZCML:

.. code:: xml

    <configure xmlns="http://namespaces.zope.org/zope">
        <adapter factory=".serializer.CustomFieldSerializer" />
    </configure>


The ``json_compatible`` function recursively converts the value
to JSON compatible data, when possible.
When a value cannot be converted, a ``TypeError`` is raised.
It is recommended to pass all values through ``json_compatible``
in order to validate and convert them.

For customizing a specific field instance, a named ``IFieldSerializer``
adapter can be registered. The name may either be the full dottedname
of the field
(``plone.app.dexterity.behaviors.exclfromnav.IExcludeFromNavigation.exclude_from_nav``)
or the shortname of the field (``exclude_from_nav``).


Content listings
================

In places where content listings are returned (children of containers, members
of collections, ...), these are produced by adapting the set of objects to be
listed to ``IContentListing``.

That content listing is then used to get ``IContentListingObject`` adapters
for the individual objects, in order to get a uniform interface to access
common properties used in summaries, like URL, title and description.

Using the ``IContentListingObject`` interface a serializeable summary
representation of the objects is produced, by looking for an
``IContentListingObjectSerializer`` that can turn that
``IContentListingObject`` into a JSON compatible, compact representation.


Customization via browser layer
-------------------------------

If you wish to control that summary representation, for example to include
additional metadata, you can register an ``IContentListingObjectSerializer``
on a browser layer specific to your project:

.. code:: python

    from your.project import IProjectSpecificLayer

    from plone.app.contentlisting.interfaces import IContentListingObject
    from plone.restapi.interfaces import IContentListingObjectSerializer
    from plone.restapi.serializer.listing import ContentListingObjectSerializer
    from zope.component import adapter
    from zope.interface import implementer


    @implementer(IContentListingObjectSerializer)
    @adapter(IContentListingObject, IProjectSpecificLayer)
    class ProjectContentListingObjectSerializer(ContentListingObjectSerializer):

        def __call__(self):
            obj = self.listing_obj    # See IContentListingObject interface
            # ...
            result = super(ProjectContentListingObjectSerializer, self).__call__()
            result['extra'] = '--PROJECT SPECIFC--'
            return result

Then register the adapter in ZCML:

.. code:: xml

    <configure xmlns="http://namespaces.zope.org/zope">
        <adapter factory=".serializer.ProjectContentListingObjectSerializer" />
    </configure>


Type-specific customization
---------------------------

If you want to control the summary representation for a **specific type**,
there's a little bit of indirection needed:

You'll need to introduce an interface that inherits from
``IContentListingObject``, and is therefore more specific. For that interface
you then register an adapter that adapts your custom type and provides an
``IContentListingObject`` implementation.

That interface can then be used to register your type specific
``IContentListingObjectSerializer``:

.. code:: python

    from your.project import ICustomType

    from plone.app.contentlisting.realobject import RealContentListingObject
    from zope.interface import implementer_only


    class ICustomTypeContentListingObject(IContentListingObject):
        """Type specific IContentListingObject interface.
        """


    @implementer_only(ICustomTypeContentListingObject)
    @adapter(ICustomType)
    class CustomTypeContentListingObject(RealContentListingObject):
        """Type specific ContentListingObject implementation.

        You can inherit from the default implementation for that type of object,
        or provide your own implementation of IContentListingObject.
        """


    @implementer(IContentListingObjectSerializer)
    @adapter(ICustomTypeContentListingObject, IProjectSpecificLayer)
    class CustomTypeContentListingObjectSerializer(ContentListingObjectSerializer):

        def __call__(self):
            result = super(CustomTypeContentListingObjectSerializer, self).__call__()
            result['extra'] = '--TYPE SPECIFIC--'
            return result

Register the adapters in ZCML:

.. code:: xml

    <configure xmlns="http://namespaces.zope.org/zope">
        <adapter factory=".serializer.CustomTypeContentListingObjectSerializer" />
        <adapter factory=".serializer.CustomTypeContentListingObject" />
    </configure>
