Changelog
=========

1.0a10 (2017-03-22)
-------------------

New Features:

- Add @sharing endpoint.
  [timo,csenger,sneridagh]

- Add @vocabularies endpoint.
  [timo,csenger,sneridagh]

- Add @copy and @move endpoints.
  [buchi,sneridagh]

- Docs: Convert all HTTP examples to use sphinxcontrib-httpexample.
  [lgraf]

- Add 'addable' attribute to the @types endpoint. It specifies if the content
  type can be added to the current context. See
  https://github.com/plone/plone.restapi/issues/173.
  [jaroel]

- Add support for named IJsonSchemaProvider adapter to target a single
  field in a schema. This allows us to prevent rendering all choices in
  relatedItems. See https://github.com/plone/plone.restapi/issues/199.
  [jaroel]

- Add review_state to the folderish summary serializer.
  [sneridagh]

- Add @principals endpoint. It searches for principals and returns a list of
  users and groups that matches the query. This is aimed to be used in the
  sharing UI widget or other user/groups search widgets.
  [sneridagh]

- Add reset-password action to the @users endpoint.
  https://github.com/plone/plone.restapi/issues/158
  [timo,csenger]

Bugfixes:

- Fix coveralls reporting.
  [timo]

- Return correct @id for folderish objects created via POST.
  [lgraf]

- Fix timezone-related failures when running tests through `coverage`.
  [witsch]

- @search endpoint: Also prefill path query dict with context path.
  This will allow users to supply an argument like path.depth=1, and still
  have path.query be prefilled server-side to the context's path.
  [lgraf]

- Overhaul JSON schema generation for @types endpoint. It now returns
  fields in correct order and in their appropriate fieldsets.
  [lgraf]

- Add missing id to the Plone site serialization, related to issue #186.
  [sneridagh]

- Add missing adapter for IBytes on JSONFieldSchema generator. This fixes the
  broken /@types/Image and /@types/File endpoints.
  [sneridagh]

- Fix addable types for member users and roles assigned locally on @types
  endpoint.
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
