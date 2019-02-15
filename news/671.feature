Improved serialization/deserialization of the Plone Site root to make
possible an opt-in to support Tiles attributes on it. The @workflow endpoint
now answers an empty object instead of a 404 for the Plone Site Root object,
hiding the implementation details (the Plone Site Root has no workflow for
historical reasons) and equalizing it to the other content types, making the
API more consistent.
[sneridagh]
