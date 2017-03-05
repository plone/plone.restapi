Changelog
=========

1.0a10 (unreleased)
-------------------

Bugfixes:

- @search endpoint: Also prefill path query dict with context path.
  This will allow users to supply an argument like path.depth=1, and still
  have path.query be prefilled server-side to the context's path.
  [lgraf]

- Overhaul JSON schema generation for @types endpoint. It now returns
  fields in correct order and in their appropriate fieldsets.
  [lgraf]

- Add missing id to the Plone site serialization, related to issue #186
  [sneridagh]

1.0a9 (2017-03-03)
------------------

New Features:

- Make date and datetime fields provide a 'widget' attribute.
  [timo]

- Add documentation for types endpoint schema.
  [timo]

- Add basic groups CRUD operations in @groups endpoints
  [sneridagh]

- Make @types endpoint include a 'mode' attribute. This fixes https://github.com/plone/plone.restapi/issues/198.
  [timo]

Bugfixes:

- Fix timezone-related failures when running tests through `coverage`.
  [witsch]

- Fix queries to ensure ordering of container items by getObjectPositionInParent.
  [lgraf]


1.0a8 (2017-01-12)
------------------

New Features:

- Add simple user search capabilities in the GET @users endpoint.
  [sneridagh]

Bugfixes:

- Allow installation of plone.restapi if JWT plugin already exists. This fixes
  https://github.com/plone/plone.restapi/issues/119.
  [buchi]


1.0a7 (2016-12-05)
------------------

Bugfixes:

- Make login endpoint accessible without UseRESTAPI permission. This fixes
  https://github.com/plone/plone.restapi/issues/166.
  [buchi]


1.0a6 (2016-11-30)
------------------

New Features:

- Introduce dedicated permission required to use REST API at all
  (assigned to everybody by default).
  [lgraf]

Bugfixes:

- When token expires, PAS plugin should return an empty credential.
  [ebrehault]


1.0a5 (2016-10-07)
------------------

Bugfixes:

- Remove plone.api dependency from users service. This fixes
  https://github.com/plone/plone.restapi/issues/145.
  [timo]


1.0a4 (2016-10-05)
------------------

New Features:

- Make POST request return the serialized object.
  [timo]

- Include 'id' attribute in responses.
  [timo]


1.0a3 (2016-09-27)
------------------

New Features:

- Add @users endpoint.
  [timo]

Bugfixes:

- Fix bug where disabling the "Use Keyring" flag wasn't persisted in jwt_auth plugin.
  [lgraf]


1.0a2 (2016-08-20)
------------------

New Features:

- Implements navigation and breadcrumbs components
  [ebrehault]

- Add `widget` and support for RichText field in @types component.
  [ebrehault]

- Add fieldsets in @types
  [ebrehault]

Bugfixes:

- Disable automatic CSRF protection for @login and @login-renew endpoints:
  If persisting tokens server-side is enabled, those requests need to be allowed to cause DB writes.
  [lgraf]

- Documentation: Fixed parameter 'data' to JSON format in JWT Authentication
  documentation
  [lccruz]

- Tests: Fail tests on uncommitted changes to docs/source/_json/
  [lgraf]

- Tests: Use `freezegun` to freeze hard to control timestamps in response
  dumps used for documentation.
  [lgraf]

- Tests: Limit available languages to a small set to avoid excessive language
  lists in response dumps used for documentation.
  [lgraf]


1.0a1 (2016-07-14)
------------------

- Initial release.
  [timo,buchi,lukasgraf,et al.]
