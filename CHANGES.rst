Changelog
=========

3.4.5 (unreleased)
------------------

Bugfixes:

- Avoid ``AttributeError`` on add-on installation (fixes `#465 <https://github.com/plone/plone.restapi/issues/465>`_.
  [lukasgraf, hvelarde]

- Make search work with a path query containing a list of paths in a virtual hosting setting.
  [sunew]


3.4.4 (2018-08-31)
------------------

Bugfixes:

- Generalize the last bugfix solution for searching the userid on password
  reset requests, matching it with Plone's one. This covers all the request
  use cases.
  [sneridagh]


3.4.3 (2018-08-30)
------------------

Bugfixes:

- Add "Use UUID as user ID" support for password resets
  [sneridagh]


3.4.2 (2018-08-27)
------------------

Bugfixes:

- Add missing "Use UUID as user ID" support to POST @users endpoint on user creation.
  Also improve the userid/username chooser by using the same process as Plone does.
  This fixes: https://github.com/plone/plone.restapi/issues/586
  [sneridagh]


3.4.1 (2018-07-22)
------------------

Bugfixes:

- Make sure the default profile is installed on tiles profile installation.
  [timo]


3.4.0 (2018-07-21)
------------------

New Features:

- Add tiles profile.
  [timo]


3.3.0 (2018-07-20)
------------------

New Features:

- Return member fields based on user schema in `@users` endpoint instead of a
  fixed list of member properties.
  [buchi]


3.2.2 (2018-07-19)
------------------

Bugfixes:

- Do not include HTTP examples using data_files anymore, but move them below
  src/plone/restapi instead and use package_data to include them.
  [lgraf]

- Rename Dexterity content before adding it to a container.
  [buchi]

- Avoid hard dependency on Archetypes introduced in 3.0.0.
  This fixes `issue 570 <https://github.com/plone/plone.restapi/issues/570>`_.
  [buchi]

- Make setup.py require plone.behavior >= 1.1. This fixes #575.
  [timo]

- Fixes ``test_search`` to work with bug fixed ``plone.indexer``.
  Now ``DXTestDocument`` explicit got an attribute ``exclude_from_nav``.
  This fixes `issue 579 <https://github.com/plone/plone.restapi/issues/579>`_.
  Refers to `Products.CMFPlone Issue 2469 <https://github.com/plone/Products.CMFPlone/issues/2469>`_
  [jensens]


3.2.1 (2018-06-28)
------------------

Bugfixes:

- Require plone.schema >= 1.2.0 in setup.py for new tiles endpoint.
  [timo]

3.2.0 (2018-06-28)
------------------

New Features:

- Add tiles endpoint for getting all available content tiles and its JSONSchema.
  [sneridagh]

- Add a tiles behavior to support the new tiles implementation for plone.restapi.
  [sneridagh]

- Make sure to include HTTP examples in installed egg, so test_documentation
  tests also work against a installed release of plone.restapi.
  [lgraf]


3.1.0 (2018-06-27)
------------------

New Features:

- Plone 5.2 compatibility.
  [sunew, davisagli, timo]


3.0.0 (2018-06-26)
------------------

Breaking Changes:

- Fix object creation events. Before this fix, creation events were fired on
  empty not yet deserialized objects. Also a modified event was fired after
  deserializing e newly created object.
  Custom content deserializers now must handle the `create` keyword argument,
  which determines if deserialization is performed during object creation or
  while updating an object.
  [buchi]

- Include translated role titles in `@sharing` GET.
  [lgraf]

- Image URLs are now created using the cache optimized way. Fixes #494.
  [erral]


2.2.1 (2018-06-25)
------------------

Bugfixes:

- Fix ReST on PyPi.
  [timo]


2.2.0 (2018-06-25)
------------------

New Features:

- Document the use of the `Accept-Language` HTTP header.
  [erral]

- Translate FTI titles on `@types` endpoint. Fixes #337.
  [erral]

- Translate action name, workflow state and transition names in @history endpoint.
  [erral]

- Enhance `@workflow` endpoint to support applying transitions to all contained
  items and to set effective and expiration dates.
  [buchi]

Bugfixes:

- Make sure DX DefaultFieldDeserializer validates field values.
  [lgraf]

- Reindex AT content on PATCH. This fixes `issue 531 <https://github.com/plone/plone.restapi/issues/531>`_.
  [buchi]

- Fix change password on Plone 5.2
  [sunew]

- Plone 5.2 compatible tests.
  [sunew]


2.1.0 (2018-06-23)
------------------

New Features:

- Include translated role title in `@roles` GET.
  [lgraf]


2.0.1 (2018-06-22)
------------------

Bugfixes:

- Hide upgrades from the add-ons control panel.
  Fixes `issue 532 <https://github.com/plone/plone.restapi/issues/532>`_.
  [maurits]


2.0.0 (2018-04-27)
------------------

Breaking Changes:

- Convert all datetime, DateTime and time instances to UTC before serializing.
  [thet]

- Use python-dateutil instead of DateTime to parse date strings when de-serializing.
  [thet]

- Make `@translations` endpoint expandable
  [erral]

- Rename the results attribute in `@translations` endpoint to be 'items'
  [erral]

- Remove 'language' attribute in `@translations` endpoint from the
  top-level response entry
  [erral]

New Features:

- Expose the tagged values for widgets in the @types endpoint.
  [jaroel]

- Render subject vocabulary as items for subjects field.
  [jaroel]

- New permission for accessing user information in the GET @user endpoint
  `plone.restapi: Access Plone user information` mapped by default to Manager
  role (as it was before).
  [sneridagh]

Bugfixes:

- Add VHM support to @search
  [csenger]


1.6.0 (2018-04-17)
------------------

New Features:

- Add `expand.navigation.depth` parameter to the `@navigation` endpoint.
  [fulv, sneridagh]


1.5.0 (2018-04-03)
------------------

New Features:

- Allow users to update their own properties and password.
  [sneridagh]


1.4.1 (2018-03-22)
------------------

Bugfixes:

- Fix serialization of `Discussion Item` and `Collection` content types when
  called with `fullobjects` parameter.
  [sneridagh]


1.4.0 (2018-03-19)
------------------

New Features:

- Add expandable @actions endpoint to retrieve portal_actions.
  [csenger,timo,sneridagh]


1.3.1 (2018-03-14)
------------------

Bugfixes:

- Support null in content PATCH requests to delete a field value
  (Dexterity only). This fixes #187.
  [csenger]


1.3.0 (2018-03-05)
------------------

New Features:

- Observe the allow_discussion allowance (global, fti, object) on object
  serialization.
  [sneridagh]

- Add '@email-send' endpoint to allow authorized users to send emails to
  arbitrary addresses (Plone 5 only).
  [sneridagh]


1.2.0 (2018-02-28)
------------------

New Features:

- Allow users to get their own user information.
  [erral]

Bugfixes:

- Mark uninstall profile as non-installable.
  [hvelarde]

- Fix the use of fullobjects in Archetypes based sites @search
  [erral]

- Fix workflow translations with unicode characters.
  [Gagaro]

- Fix workflow encoding in transition endpoint.
  [Gagaro]


1.1.0 (2018-01-24)
------------------

New Features:

- Add '@email-notification' endpoint to contact the site owner via email.
  (Plone 5 only)
  [sneridagh]

Bugfixes:

- Remove warning about alpha version from docs.
  [timo]


1.0.0 (2018-01-17)
------------------

Bugfixes:

- Remove deprecated getSiteEncoding import.
  [timo]

- Build documentation on Plone 5.0.x (before: Plone 4.3.x).
  [timo]


1.0b1 (2018-01-05)
------------------

Breaking Changes:

- Rename 'url' attribute on navigation / breadcrumb to '@id'.
  [timo]

New Features:

- Allow client to ask for the full representation of an object after creation
  by setting the 'Prefer' header on a PATCH request.
  [Gagaro]

- Support deserialization of a relationChoice field using the contents of the
  serialization (enhanced by the serializer) output.
  [sneridagh]

- Allow properties when adding a user.
  This allows setting the fullname by anonymous users.
  [jaroel]

- Add support for IContextSourceBinder vocabularies on JSON schema Choice
  fields adapters.
  [sneridagh]

- Add upgrade guide.
  [timo]

Bugfixes:

- Fix issue where POST or PATCH a named file with a download link would
  always return self.context.image, not the actual file.
  [jaroel]

- Fix DateTimeDeserializer when posting None for a non-required field.
  [jaroel]

- Fixed 'required' for DateTime fields.
  [jaroel]

- Batching: Preserve list-like query string params when canonicalizing URLs.
  [lgraf]

- Fixed NamedFieldDeserializer to take a null to remove files/images.
  [jaroel]

- Fixed NamedFieldDeserializer to validate required fields.
  [jaroel]

- Prevent a fatal error when we get @workflow without permission to get
  review_history worfklow variable.
  [thomasdesvenain]

- Make user registration work as default Plone behavior by adding the Member
  role to the user.
  [sneridagh]


1.0a25 (2017-11-23)
-------------------

Breaking Changes:

- Remove @components navigation and breadcrumbs. Use top level @navigation and
  @breadcrumb endpoints instead.
  [timo]

- Remove "sharing" attributes from GET response.
  [timo,jaroel]

- Convert richtext using .output_relative_to. Direct conversion from RichText
  if no longer supported as we *always* need a context for the ITransformer.
  [jaroel]

New Features:

- Add fullobjects parameter to content GET request.
  [timo]

- Include descriptions of modified fields in object-modified event.
  [buchi]

- Add uninstall profile
  [davilima6]

- Add `include_items` option to `SerializeFolderToJson`.
  [Gagaro]

Bugfixes:

- Fix error messages for password reset (wrong user and wrong password).
  [csenger]

- Fix #440, URL and @id wrong in second level get contents call for folderish
  items.
  [sneridagh]

- Fix #441, GET in a folderish content with 'fullobjects' is
  including all items recursively.
  [sneridagh]

- Fix #443, Ensure the userid returned by `authenticateCredentials` is a byte string and not unicode.
  [Gagaro]


1.0a24 (2017-11-13)
-------------------

New Features:

- Add 'is_editable' and 'is_deletable' to the serialization of comments
  objects. Also refactored the comments endpoint to DRY.
  [sneridagh]

- Improve is_folderish property to include Plone site and AT content types
  [sneridagh]

Bugfixes:

- Cover complete use cases of file handling in a content type. This includes
  removal of a image/file and being able to feed the PATCH endpoint with the
  response of a GET operation the image/file fields without deleting the
  existing value.
  [sneridagh]


1.0a23 (2017-11-07)
-------------------

Bugfixes:

- Fix JWT authentication for users defined in the Zope root user folder.
  This fixes https://github.com/plone/plone.restapi/issues/168 and
  https://github.com/plone/plone.restapi/issues/127.
  [buchi]

- Fix datetime deserialization for timezone aware fields.
  This fixes https://github.com/plone/plone.restapi/issues/253
  [buchi]


1.0a22 (2017-11-04)
-------------------

New Features:

- Add @translations endpoint
  [erral]

- Include title in site serialization.
  [buchi]

- Include is_folderish property on GET request responses. Fixes #327.
  [sneridagh]


Bugfixes:

- Strip spaces from TextLine values to match z3c.form implementation.
  [jaroel]

- Disallow None and u'' when TextLine is required. Refs #351.
  [jaroel]

- Make getting '/@types/{type_id}' work for non-DX types, ie "Plone Site".
  [jaroel]

- Remove Products.PasswortResetTool from setup.py since it is
  a soft dependency. It is included in Plone >= 5.1.
  [tomgross]

- Update pytz to fix travis builds
  [sneridagh]


1.0a21 (2017-09-23)
-------------------

New Features:

- Add support for expandable elements. See http://plonerestapi.readthedocs.io/en/latest/expansion.html for details.
  [buchi]

- Translate titles in @workflow.
  [csenger]

- Add endpoints for locking/unlocking. See http://plonerestapi.readthedocs.io/en/latest/locking.html for details.
  [buchi]

- Add @controlpanels endpoint.
  [jaroel, timo]

Bugfixes:

- Fix ZCML load order issue by explicitly loading permissions.zcml from CMFCore.
  [lgraf]

- Fix @id values returned by @search with 'fullobjects' option
  [ebrehault]

- Re-add skipped tests from @breadcrumbs and @navigation now that expansion
  is in place.
  [sneridagh]


1.0a20 (2017-07-24)
-------------------

Bugfixes:

- Support content reordering on the site root.
  [jaroel]

- Support setting Layout on the site root.
  [jaroel]

- Add clarification when using SearchableText parameter in plone.restapi to avoid confusions
  [sneridagh]


1.0a19 (2017-06-25)
-------------------

New Features:

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

- Don't list non-DX types in @types endpoint.
  Refs https://github.com/plone/plone.restapi/issues/150
  [jaroel]


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

- Add @translations endpoint
  [erral]

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
