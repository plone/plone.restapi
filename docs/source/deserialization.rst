Deserialization
===============

It's worth to note an special case when deserializing Datetimes objects, and how plone.restapi will handle them.

Although not supported by Plone itself yet, plone.restapi will store all the Datetimes that will be handling along with its timezone converted to UTC.
This will provide a common ground for all the datetimes operations.

There is a special case when using datetimes objects in p.a.event, and its behavior is different due to implementation differences for versions 1.x (Plone 4) and 2.x and above (Plone 5).

.. warning::
  In case of using zope.schema date validators you should also use a datetime object that also contains offset-aware object as the validator value.

.. note::
  This does not apply in case that you are using Plone 4 with no Dexterity support at all or not p.a.event installed.

p.a.event 1.x in Plone 4
------------------------

The implementation of p.a.event in 1.x requires to provide a `timezone` schema property along with the Event type information, otherwise the creation fails, because it's a required field, like this::

.. code-block:: json

  {
    "@type": "Event",
    "id": "myevent2",
    "title": "My Event",
    "start": "2018-01-01T10:00:00",
    "end": "2018-01-01T12:00:00",
    "timezone": "Asia/Saigon"
  }

The final stored datetime takes this field into account and adds the correct offset to the content type (abbreviated JSON response)::

.. code-block:: json

  {
    "@id": "http://localhost:55001/plone/folder1/myevent2",
    "@type": "Event",
    "UID": "bcfc3914ea174cc1aa8042147edfa33a",
    "creators": ["admin"],
    "description": "",
    "end": "2018-01-01T12:00:00+07:00",
    "id": "myevent2",
    "start": "2018-01-01T10:00:00+07:00",
    "timezone": "Asia/Saigon",
    "title": "My Event",
    }

and builds the `start` and `end` fields with the proper timezone, depending on the `timezone` field. It also returns the datetime object with the proper timezone offset.

If using Plone 4 and p.a.event 1.x you should construct the Event type using this approach, otherwise the Event object will be created with a wrong timezone.

This approach was counterintuitive, and thus, it was changed it Plone 5 version of p.a.event.

p.a.event 2.x in Plone 5
------------------------

The implementation of p.a.event in 2.x no longer requires to provide a `timezone` schema property, because the timezone is computed taking the timezone already existent in dates supplied::

.. code-block:: json

  {
    "@type": "Event",
    "id": "myevent2",
    "title": "My Event",
    "start": "2018-01-01T10:00:00+07:00",
    "end": "2018-01-01T12:00:00+07:00",
  }

You should pass the timezone information in the ISO8601 format, otherwise the system will fallback to UTC. The response given is also computed given the timezone information supplied, but this time it's UTC based:

.. code-block:: json

  {
    "@id": "http://localhost:55001/plone/folder1/myevent2",
    "@type": "Event",
    "UID": "4c031960718246db86c97685f83047ee",
    "creators": ["admin"],
    "description": "",
    "end": "2018-01-01T05:00:00+00:00",
    "id": "myevent2",
    "start": "2018-01-01T03:00:00+00:00",
    "title": "My Event",
  }

This approach is better because all Javascript serializers/deserializers works with UTC based dates (e.g. .toJSON Javascript API).
