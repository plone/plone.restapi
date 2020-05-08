.. _types-schema:

Types Schema
============

A detailed list of all available `Zope Schema <http://docs.zope.org/zope.schema/>`_  field types and their corresponding representation as `JSON Schema <http://json-schema.org/>`_ .

TextLine
--------

Zope Schema::

    zope.schema.TextLine(
        title=u'My field',
        description=u'My great field',
        default=u'foobar'
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'default': u'foobar',
    }


Text
----

Zope Schema::

    zope.schema.Text(
        title=u'My field',
        description=u'My great field',
        default=u'Lorem ipsum dolor sit amet',
        min_length=10,
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'widget': 'textarea',
        'default': u'Lorem ipsum dolor sit amet',
        'minLength': 10,
    }


Bool
----

Zope Schema::

    zope.schema.Bool(
        title=u'My field',
        description=u'My great field',
        default=False,
    )

JSON Schema::

    {
        'type': 'boolean',
        'title': u'My field',
        'description': u'My great field',
        'default': False,
    }


Float
-----

Zope Schema::

    zope.schema.Float(
        title=u'My field',
        description=u'My great field',
        min=0.0,
        max=1.0,
        default=0.5,
    )

JSON Schema::

    {
        'minimum': 0.0,
        'maximum': 1.0,
        'type': 'number',
        'title': u'My field',
        'description': u'My great field',
        'default': 0.5,
    }


Decimal
-------

Zope Schema::

    zope.schema.Decimal(
        title=u'My field',
        description=u'My great field',
        min=Decimal(0),
        max=Decimal(1),
        default=Decimal(0.5),
    )

JSON Schema::

    {
        'minimum': 0.0,
        'maximum': 1.0,
        'type': 'number',
        'title': u'My field',
        'description': u'My great field',
        'default': 0.5,
    },


Int
---

Zope Schema::

    zope.schema.Int(
        title=u'My field',
        description=u'My great field',
        min=0,
        max=100,
        default=50,
    )

JSON Schema::

    {
        'minimum': 0,
        'maximum': 100,
        'type': 'integer',
        'title': u'My field',
        'description': u'My great field',
        'default': 50,
    }


Choice
------

Zope Schema::

    zope.schema.Choice(
        title=u'My field',
        description=u'My great field',
        vocabulary=self.dummy_vocabulary,
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'enum': ['foo', 'bar'],
        'enumNames': ['Foo', 'Bar'],
        'choices': [('foo', 'Foo'), ('bar', 'Bar')],
    }


List
----

Zope Schema::

    zope.schema.List(
        title=u'My field',
        description=u'My great field',
        min_length=1,
        value_type=schema.TextLine(
            title=u'Text',
            description=u'Text field',
            default=u'Default text'
        ),
        default=['foobar'],
    )

JSON Schema::

    {
        'type': 'array',
        'title': u'My field',
        'description': u'My great field',
        'default': ['foobar'],
        'minItems': 1,
        'uniqueItems': False,
        'additionalItems': True,
        'items': {
            'type': 'string',
            'title': u'Text',
            'description': u'Text field',
            'default': u'Default text',
        }
    },


Tuple
-----

Zope Schema::

    field = zope.schema.Tuple(
        title=u'My field',
        value_type=schema.Int(),
        default=(1, 2),
    )

JSON Schema::

    {
        'type': 'array',
        'title': u'My field',
        'description': u'',
        'uniqueItems': True,
        'additionalItems': True,
        'items': {
            'title': u'',
            'description': u'',
            'type': 'integer',
        },
        'default': (1, 2),
    }


Set
---

Zope Schema::

    field = zope.schema.Set(
        title=u'My field',
        value_type=schema.TextLine(),
    )

JSON Schema::

    {
        'type': 'array',
        'title': u'My field',
        'description': u'',
        'uniqueItems': True,
        'additionalItems': True,
        'items': {
            'title': u'',
            'description': u'',
            'type': 'string',
        }
    }


List of Choices
---------------

Zope Schema::

    field = zope.schema.List(
        title=u'My field',
        value_type=schema.Choice(
            vocabulary=self.dummy_vocabulary,
        ),
    )

JSON Schema::

    {
        'type': 'array',
        'title': u'My field',
        'description': u'',
        'uniqueItems': True,
        'additionalItems': True,
        'items': {
            'title': u'',
            'description': u'',
            'type': 'string',
            'enum': ['foo', 'bar'],
            'enumNames': ['Foo', 'Bar'],
            'choices': [('foo', 'Foo'), ('bar', 'Bar')],
        }
    }


Object
------

Zope Schema::

    zope.schema.Object(
        title=u'My field',
        description=u'My great field',
        schema=IDummySchema,
    )

JSON Schema::

    {
        'type': 'object',
        'title': u'My field',
        'description': u'My great field',
        'properties': {
            'field1': {
                'title': u'Foo',
                'description': u'',
                'type': 'boolean'
            },
            'field2': {
                'title': u'Bar',
                'description': u'',
                'type': 'string'
            },
        }
    },


RichText (plone.app.textfield)
------------------------------

Zope Schema::

    from plone.app.textfield import RichText
    field = RichText(
        title=u'My field',
        description=u'My great field',
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'widget': 'richtext',
    }


Date
----

Zope Schema::

    zope.schema.Date(
        title=u'My field',
        description=u'My great field',
        default=date(2016, 1, 1),
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'default': date(2016, 1, 1),
        'widget': u'date',
    }


DateTime
--------

Zope Schema::

    zope.schema.Datetime(
        title=u'My field',
        description=u'My great field',
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'widget': u'datetime',
    }


Email
-----

Zope Schema::

    plone.schema.Email(
        title=u'My field',
        description=u'My great field',
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'widget': u'email',
    }


Password
--------

Zope Schema::

    zope.schema.Password(
        title=u'My field',
        description=u'My great field',
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'widget': u'password',
    }


URI
---

Zope Schema::

    zope.schema.URI(
        title=u'My field',
        description=u'My great field',
    )

JSON Schema::

    {
        'type': 'string',
        'title': u'My field',
        'description': u'My great field',
        'widget': u'url',
    }
