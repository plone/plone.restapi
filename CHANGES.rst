Changelog
=========

1.0a19 (2017-06-25)
-------------------

- Implement tus.io upload endpoint.
  [buchi]


1.0a18 (2017-06-14)
-------------------

New Features:

- Add "&fullobject" parameter in @search to retrieve full objects
  [ebrehault]

Bugfixes:

- Tweaks to README.rst
  [tkimnguyen]


1.0a17 (2017-05-31)
-------------------

Breaking Changes:

- Change RichText field value to use 'output' instead of 'raw' to fix inline
  paths. This fixes #302.
  [erral]

New Features:

- Automatically publish docker images on hub.docker.com.
  [timo]

Bugfixes:

- Docs: Fix batching example request/response.
  [lgraf]


1.0a16 (2017-05-23)
-------------------

New Features:

- Add @comments endpoint.
  [jaroel,timo,pjoshi]

- Add @roles endpoint to list defined global roles.
  [jaroel]

- Add JSON schema to @registry listing.
  [jaroel]

- Allow to manipulate the group membership in the @groups endpoint.
  [jaroel]

- List and mutate global roles assigned to a user in the @users endpoint.
  [jaroel]

Bugfixes:

- Bind schema field to context to handle context vocabularies. #389
  [csenger]

- The inherit flag was the wrong way around.
  Blocked inherit showed up as non-blocked.
  [jaroel]


1.0a15 (2017-05-15)
-------------------

New Features:

- Reorder children in a item using the content endpoint.
  [jaroel]

- Add batched listing of registry entries to @registry endpoint.
  [jaroel]


1.0a14 (2017-05-02)
-------------------

New Features:

- Add @history endpoint.
  [jaroel]

Bugfixes:

- Fix the @move endpoint fails to return 403 when the user don't have proper
  delete permissions over the parent folder.
  [sneridagh]


1.0a13 (2017-04-18)
-------------------

New Features:

- Add support for a 'search' parameter to @sharing. This returns additional
  principals in 'entries', also flagging the acquired and inherited fields.
  [jaroel]

- Add support for setting/modifying 'layout' on DX and AT content endpoints.
  [jaroel]

- Add support for getting the defined layouts on the root types endpoint.
  [jaroel]

Bugfixes:

- Add the title to the workflow history in the @workflow endpoint.
  This fixes #279.
  [sneridagh]

- Don't fetch unnecessary PasswordResetTool in Plone 5.1
  [tomgross]


1.0a12 (2017-04-03)
-------------------

Bugfixes:

- Handle special case when user @move content that cannot delete returning
  proper 403
  [sneridagh]


1.0a11 (2017-03-24)
-------------------

Bugfixes:

- Remove zope.intid dependency from copy/move endpoint. Remove plone.api
  dependency from principals endpoint. Make
  ChoiceslessRelationListSchemaProvider available only if z3c.relationfield
  is installed. This fixes https://github.com/plone/plone.restapi/issues/288
  [erral]

- Remove unittest2 imports from tests.
  [timo]

- Add Products.PasswortResetTool to dependencies. This dependency is gone in
  Plone 5.1.
  [timo]

- Make import of LocalrolesModifiedEvent conditional, so plone.restapi
  doesn't prevent Plone 4.3 deployments < 4.3.4 from booting.
  [lgraf]


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
