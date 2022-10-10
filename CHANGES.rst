Changelog
=========

.. You should *NOT* be adding new change log entries to this file.
   You should create a file in the news directory instead.
   For helpful instructions, please see:
   https://github.com/plone/plone.releaser/blob/master/ADD-A-NEWS-ITEM.rst

.. towncrier release notes start

8.30.0 (2022-10-02)
-------------------

New features:


- Add link integrity support for blocks
  [cekk] (#953)


Internal:


- Plone 6 as first class citizen in builds and CI. Remove non-supported Python versions. Add 3.10 for Plone 6.
  [sneridagh] (#1503)


8.29.0 (2022-10-01)
-------------------

New features:


- Add @userschema endpoint for getting the user schema.
  [sneridagh] (#706)
- Add @transactions endpoint to fetch transactions that have been made through the Plone website.
  [@MdSahil-oss] (#1505)


Bug fixes:


- The ``@controlpanels/usergroup`` does not work for Plone 5 since it does not exist there. Bring back the missing `title` just for Plone 5.
  [sneridagh] (#1501)


8.28.0 (2022-09-29)
-------------------

New features:


- Improve performance of serializing image scales. [davisagli] (#1498)


Bug fixes:


- Revert "When an id is specified explicitly in the content POST endpoint,
  return a 400 error response if it is invalid or unavailable."
  The fix was incorrect and disallowing ids that should be allowed.
  [davisagli] (#1488)
- Increase the length of passwords used in tests. [davisagli] (#1492)
- Use json_compatible when serializing users in @users endpoint
  [erral] (#1493)


Documentation:


- Reorganize navigation. [stevepiercy] (#1486)
- Fix Google redirect and hyphenation of word. [stevepiercy] (#1495)


8.27.0 (2022-09-14)
-------------------

New features:


- Added @aliases endpoint with GET/POST/DELETE
  [iulianpetchesi] (#1393)


Bug fixes:


- When an `id` is specified explicitly in the content POST endpoint,
  return a 400 error response if it is invalid or unavailable.
  [davisagli] (#1487)


8.26.0 (2022-09-10)
-------------------

New features:


- Add @portrait endpoint
  [sneridagh] (#1480)


Bug fixes:


- Add portrait to the docs toctree to fix build warning. [stevepiercy] (#1485)


8.25.1 (2022-09-02)
-------------------

Bug fixes:


- Fix the category of the 'Users and groups settings' controlpanel adapter
  [sneridagh] (#1482)


8.25.0 (2022-08-31)
-------------------

New features:


- Add support for importing profiles in @addons endpoint
  [sneridagh] (#1479)


Bug fixes:


- Fix @registry endpoint Object of type datetime is not JSON serializable
  [iulianpetchesi] (#1189)
- Fixed small documentation for error code 404
  [rohnsha] (#1430)
- Handle subblocks in site root serializer for Plone 5.x
  [erral] (#1449)
- Do not hard depend on `plone.app.iterate`. It is not an direct core package and might not be available.
  [jensens] (#1461)
- Sanitise user id when checking for portrait [instification] (#1466)


8.24.1 (2022-08-04)
-------------------

Bug fixes:


- Fix of users endpoint for Membrane users. [ksuess] (#1459)


8.24.0 (2022-07-15)
-------------------

New features:


- Add support to search for fullname, email, id on the @users endpoint with "?search=" [ksuess] (#1443)

Bug fixes:


- Tests: add names to behaviors.  [maurits] (#169)


8.23.0 (2022-06-23)
-------------------

New features:


- Include users data in groups while retrieving @groups
  [@nileshgulia1] (#1325)
- Added 'View comments' and 'Reply to item' permission to discussion [@razvanMiu] (#1327)
- better error logging for term lookup errors
  [ajung] (#1365)
- Documentation was converted to MyST from reStructuredText. [stevepiercy] (#1375)
- Move caching rulesets to the ZCML where the endpoints are defined.
  [jensens] (#1414)
- List Users (@users): Add groups [ksuess]
  List Users (@users): Support filtering by groups [ksuess] (#1419)
- Fix: Update group: Preserve title and description. [ksuess] (#1424)
- Add UsersGroupsSettings to set of control panels. [ksuess]
  Move configlet UsersGroupsSettings to correct group (Volto control panel group "Users and Groups") [ksuess] (#1436)


Bug fixes:


- Test-only fix: normalize white space in html in some tests.
  Needed to not fail with newer plone.outputfilters.
  [maurits] (#49)
- Tests: patch unique url for scale in old or new way.
  This is only in serializer tests for images.
  [maurits] (#57)
- Make the PAS plugin compatible with ``PyJWT`` 1 and 2.
  [jensens, maurits] (#1193)
- Fix tests for changes in displayed_types. See https://github.com/plone/Products.CMFPlone/issues/3486
  [pbauer] (#1359)
- Use JSON instead of JSON Schema for code samples. [stevepiercy] (#1379)
- Control panels and translations are supported in Plone 5 or greater. [stevepiercy] (#1380)
- Add html_meta tags and values for better SEO. [stevepiercy] (#1382)
- Update demo site to 6.demo.plone.org in README.rst. [stevepiercy] (#1383)
- Fixed timestamp calculation in history service on Python 3.10.
  [maurits] (#1391)
- Fix empty .resp in docs of PATCH controlpanel (#1396)
- Translate addon titles on @addon controlpanel
  [erral] (#1412)
- Do not break path2uid with some edge-cases.
  [cekk] (#1428)
- Sort the roles in the user serializer.
  [maurits] (#1452)


Internal:


- Add naming best practices for URL Attributes (singular vs plural) to the docs
  [tisto] (#1295)
- Enable Google Analytics 4 [stevepiercy] (#1404)
- fixed broken make task docs-linkcheckbroken (#1421)
- Fix broken link to Python requests library docs. [stevepiercy] (#1438)


8.22.0 (2022-04-08)
-------------------

New features:


- Fix broken links. Add `make netlify` as a build target to preview changes to docs only. Prepare docs for import into main Plone documentation without significant changes. Use sphinx-book-them as theme. [stevepiercy] (#1337)


Bug fixes:


- Return proper error message when trying to create a content object with a wrong @type parameter. [tisto] (#1188)
- Fix the link in the GitHub menu item "suggest edit" to point to master branch. [stevepiercy] (#1346)
- Fix the redirect link for upc.edu to /en. [stevepiercy] (#1351)
- Fix testing matrix to use correct combos of Python and Plone.
  [maurits] (#1356)


8.21.2 (2022-02-21)
-------------------

Bug fixes:


- Restrict unlinking on Language Root Folders
  [sneridagh] (#1332)


8.21.1 (2022-02-21)
-------------------

Bug fixes:


- Improve handling of linking translations taking into account the state of the target. Restricting it completely for LRFs. Adding a transaction note to the action if it succeeds.
  [sneridagh] (#1329)


8.21.0 (2022-01-25)
-------------------

New features:


- Enhance @addons endpoint to return a list of upgradeable addons.
  [sneridagh] (#1319)


8.20.0 (2022-01-19)
-------------------

New features:


- Add support for DX Plone Site root in Plone 6. Remove blocks behavior hack for site root in Plone 6.
  [sneridagh] (#1219)


8.19.0 (2022-01-19)
-------------------

New features:


- Add support for multilingual language independent fields in field serialization
  [sneridagh] (#1316)


Internal:


- Update build to Plone 6 alpha 2
  [sneridagh] (#1312)


8.18.1 (2022-01-06)
-------------------

Internal:


- Be permissive when testing the schema of the querystring endpoint [reebalazs] (#1307)


8.18.0 (2022-01-03)
-------------------

New features:


- Improve vocabulary endpoint when asking for a list of tokens adding resilience and deprecation warning
  [sneridagh] (#1298)
- Expandable params as list and deprecations for list as comma separated
  [sneridagh] (#1300)


Bug fixes:


- Do not break in recursive transition when children already are in destination state. [cekk] (#1291)
- Resolve the bulk of deprecation and resource leak warnings when running the full test
  suite.
  [rpatterson] (#1302)


8.17.0 (2021-12-21)
-------------------

New features:


- Enhance the vocabularies serializer to accept a list of tokens
  [sneridagh] (#1294)


Bug fixes:


- SearchableText indexer should maintain the order of the blocks
  [ericof] (#1292)


8.16.2 (2021-12-03)
-------------------

Bug fixes:


- Revert "Improve support for missing_value and default story" because it breaks multilingual
  [timo] (#1289)


8.16.1 (2021-11-30)
-------------------

Bug fixes:


- Improve support and meaning for `default` and `missing_value` in serializers/deserializers
  [sneridagh] (#1282)


8.16.0 (2021-11-29)
-------------------

New features:


- Enable table blocks indexing [cekk] (#1281)


8.15.3 (2021-11-29)
-------------------

Bug fixes:


- Types service: Do not consider TypeSchemaContext as a valid context
  [ericof] (#1278)
- Improve error status code in vocabularies endpoint refactor
  [sneridagh] (#1284)


8.15.2 (2021-11-24)
-------------------

Bug fixes:


- Adjust restrictions of vocabularies endpoint [ksuess] (#1258)


8.15.1 (2021-11-24)
-------------------

Bug fixes:


- Fix schema generation when /@types/ is used in a context. [ericof] (#1271)


8.15.0 (2021-11-23)
-------------------

New features:


- Return non-batched vocabularies given a query param ``b_size=-1``
  [sneridagh] (#1264)


Bug fixes:


- Remove all traces of ``Products.CMFQuickInstaller``.
  It was removed in Plone 5.2.
  BBB code was in ``plone.app.upgrade`` only.
  Plone with Restapi broke if ``plone.app.upgrade` was not available, like when dependening on ``Products.CMFPlone`` only.
  [jensens] (#1267)
- Fix installation of JWT PAS plugin with default profile. [jensens] (#1269)


8.14.0 (2021-11-11)
-------------------

New features:


- Add root (INavigationRoot) for the current object information in @translations endpoint
  [sneridagh] (#1263)


8.13.0 (2021-11-05)
-------------------

New features:


- Implement IJSONSummarySerializerMetadata allowing addons to extend the metadata returned by Summary serializer.
  [ericof] (#1250)
- Enable usage of metadata_fields also for POST calls [cekk] (#1253)


8.12.1 (2021-10-14)
-------------------

Bug fixes:


- Fix wrong @id attribute on the Plone root serialization when using the new ++api++ traversal (introduced in plone.rest 2.0.0)
  [sneridagh] (#1248)


8.12.0 (2021-10-11)
-------------------

New features:


- Add missing backend logout actions for the @logout endpoint (delete cookie, etc)
  [sneridagh] (#1239)


8.11.0 (2021-09-29)
-------------------

New features:


- Make masking specific validation errors configurable in DX DeserializeFromJson. [fredvd] (#1211)


Bug fixes:


- Normalize unstable generated behavior names in http-examples output.
  No longer hardcode port 55001 for the tests.
  [maurits] (#1226)
- Avoid `UnboundLocalError` or duplicates in results when using `@search` endpoint and a brain is orphan or a `KeyError` occurs during result serialization.
  [gbastien] (#1231)


8.10.0 (2021-09-24)
-------------------

New features:


- Update default allow_headers CORS to include: Lock-Token [@avoinea] (#1181)
- @types endpoint also returns if a content type is immediately addable in the given context
  [ericof] (#1228)


Bug fixes:


- Fix @users endpoint to use acl_users.searchResults instead of portal_membership.listMembers
  [ericof] (#1199)
- Fix testing of a checkout instead of a released package.
  [maurits] (#1213)
- Fix @users endpoint to return list of users ordered by fullname property
  [ericof] (#1222)


8.9.1 (2021-08-27)
------------------

Bug fixes:


- Fixes values not being stored during content creation if value is equal to the one returned by defaultFactory.
  [ericof] (#1207)


8.9.0 (2021-08-25)
------------------

New features:


- Refactor `@lock` endpoint based on CRUD operations [@avoinea] (#1181)


8.8.1 (2021-08-20)
------------------

Bug fixes:


- Fix @vocabularies endpoint to search in translated term titles
  [sneridagh] (#1204)


8.8.0 (2021-08-20)
------------------

New features:


- Add resolveuid support to Link content type ``remoteUrl`` field.
  [sneridagh] (#1197)


Bug fixes:


- Updated tests to not fail when the Plone Site root is dexterity.
  [jaroel] (#2454)


8.7.1 (2021-08-03)
------------------

Bug fixes:


- Do not break @workflow endpoint for contents without workflow [cekk] (#1184)
- Do not break @workflow endpoint when trying to change the state of a content without workflow [cekk] (#1190)


8.7.0 (2021-07-19)
------------------

New features:


- Improve extensibility story for resolveUID field serializer/deserializer
  [sneridagh] (#1179)


8.6.1 (2021-07-16)
------------------

Bug fixes:


- Wrong deserialization if the path does not exist but is matched via acquisition
  [sneridagh] (#1176)


8.6.0 (2021-07-13)
------------------

New features:


- Set UID of a content during creation if the user has Manage Portal permission.
  [ericof] (#497)


8.5.0 (2021-07-09)
------------------

New features:


- Remove Python 2, Plone 4.3, and 5.1 code.
  [ericof] (#1140)


8.4.2 (2021-07-08)
------------------

Bug fixes:


- In src run `find . -name "*.py"|xargs pyupgrade --py36-plus`.
  Then run black and remove six import leftovers.
  [jensens] (#1162)
- Fix link content serialization when url points to local content but it does not exist
  [sneridagh] (#1167)
- Fix navigation service not using nav_title metadata.
  [ericof] (#1169)


8.4.1 (2021-07-07)
------------------

Bug fixes:


- Fix interpolation variable present in response after serialization
  [sneridagh] (#1164)


8.4.0 (2021-07-06)
------------------

New features:


- Pass through field attribute 'widget' for field Dict [ksuess] (#1153)


Bug fixes:


- Use security decorators in PAS plugin. [jensens] (#1155)
- Drop coding magic first line. Coding magic is no longer needed in Python 3, except if different from utf-8. [jensens] (#1156)
- Fix PAS plugin ZMI markup for Zope4+. [jensens] (#1157)
- Eliminate non-pythonic 'return None' usage. [jensens] (#1158)
- Provide value_type of plone.schema / zope.schema Dict field [ksuess] (#1159)


8.3.2 (2021-07-05)
------------------

Bug fixes:


- Fix navigation endpoint sort by adding default `sort_on='getObjPositionInParent'` to the query.  @valipod @tiberiuichim (#1107)


8.3.1 (2021-07-02)
------------------

Bug fixes:


- Unify ZMI, HTML form, and API login. @rpatterson (#1141)


8.3.0 (2021-06-07)
------------------

New features:


- Add current state and translation to the @workflow endpoint
  [sneridagh] (#1146)


Bug fixes:


- Remove code to support Python 2, Plone 4.3/5.0/5.1 [timo] (#1140)
- Remove unecessary check for plone.app.iterate which breaks the @components attributes. [timo] (#1148)


8.2.0 (2021-06-02)
------------------

New features:


- Add working copy (p.a.iterate) support
  [sneridagh] (#1132)


8.1.0 (2021-05-27)
------------------

New features:


- Add support for volto-slate blocks: use resolveuid for internal links, index slate blocks in the catalog, support block transforms. @tiberiuichim (#1125)


Bug fixes:


- Fixed a deprecation warning when importing UnrestrictedUser from AccessControl (#1129)



Internal:

- Format zcml files with collective.zpretty. Add zpretty Github workflow. @tiberiuichim


8.0.0 (2021-05-14)
------------------

Breaking changes:


- Drop support for Python 2 and Plone 5.1 and 4.3. Plone RESTAPI >= 8 supports Python 3 and Plone 5.2/6.x only. [timo] (#1121)


7.3.5 (2021-05-03)
------------------

Bug fixes:


- Fix ``@workflow`` when executing user has no permissions to access ``review_history`` in target state.
  [deiferni] (#999)


7.3.4 (2021-04-30)
------------------

Bug fixes:


- Fix ``@history`` when full history is empty.
  [deiferni] (#1113)


7.3.3 (2021-04-29)
------------------

Bug fixes:


- Fix ``@querystring-search`` endpoint with correct sort_order
  @mamico (#1108)


7.3.2 (2021-04-07)
------------------

Bug fixes:


- Fix ``@search`` endpoint with use_site_search_settings flag, for VHM PhysicalRoot
  scenarios
  @tiberiuichim (#1105)


7.3.1 (2021-03-27)
------------------

Bug fixes:


- Fixes if old p.schema is used
  [sneridagh] (#1103)


7.3.0 (2021-03-25)
------------------

New features:


- Adjust JSONField adapter to include widget name to use in serialization
  [sneridagh] (#1089)


Bug fixes:


- Fixes build was using the released version
  [sneridagh] (#1090)


7.2.1 (2021-03-22)
------------------

Bug fixes:


- @contextnavigation endpoint does not honor nav_title index
  [sneridagh] (#1092)


7.2.0 (2021-03-18)
------------------

New features:


- Allow block transforms to run in "subblocks", discovered as the ``blocks`` field (or alternatively, ``data.blocks``) in a block value. (#1085)


7.1.0 (2021-03-17)
------------------

New features:


- Allow passing ``use_site_search_settings=1`` in the ``@search`` endpoint request, to follow Plone's ``ISearchSchema`` settings. (#1081)


Bug fixes:


- Do not log "No such index" warnings for knonw indexes like metadata_fields @cekk (#987)
- Respect "Access inactive portal content" permission in @search endpoint [cekk] (#1066)
- Add GSM unsubscribe for test registered adapters in block transformer tests @tiberiuichim (#1083)
- Pin some package versions to fix buildout @tiberiuichim (#1086)


7.0.0 (2021-02-20)
------------------

- Re-release 7.0.0b8 as 7.0.0 final. [timo]


7.0.0b8 (2021-02-19)
--------------------

New features:


- Mark restapi 7 with a zcml feature flag: ``plonerestapi-7``
  [sneridagh] (#1068)
- Add a couple of additional tests for resolveuid feature reassurance
  [sneridagh] (#1072)


Bug fixes:


- Avoid duplicate fields within DX RestAPI
  [avoinea] (#1073)


7.0.0b7 (2021-02-10)
--------------------

New features:


- Add ``root`` element to the @breadcrumbs endpoint
  [sneridagh] (#1064)


Bug fixes:


- Remove ``escape``'d titles
  [sneridagh] (#1061)


7.0.0b6 (2021-02-09)
--------------------

Bug fixes:


- Do not break if some custom code provides an alias for Products.Archetypes (#1004)
- Handle missing review_state value in @navigation endpoint for items without a workflow [cekk] (#1060)


7.0.0b5 (2021-02-03)
--------------------

Bug fixes:


- Fix transform object_browser href smartfield not working as expected
  [sneridagh] (#1058)


7.0.0b4 (2021-02-01)
--------------------

Bug fixes:


- Fix href smart field in transformers do not cover the object_widget use case
  [sneridagh] (#1054)


7.0.0b3 (2021-01-26)
--------------------

New features:


- Add new @contextnavigation endpoint.
  [tiberiuichim] (#1042)
- Refactor navigation endpoint, add new ``nav_title`` attribute
  [sneridagh] (#1047)
- Add nav_title attribute to breadcrumbs endpoint
  [sneridagh] (#1049)
- Unify nav_title and title in navs
  [sneridagh] (#1051)


Bug fixes:


- Fix ``@id`` when content query has no ``fullbojects``
  [sneridagh] (#837)


7.0.0b2 (2021-01-25)
--------------------

New features:


- Add serializer/deserializer for remoteUrl Link's field [cekk] (#1005)


7.0.0b1 (2021-01-08)
--------------------

New features:


- Register blocks transformers also for Site Root
  [cekk] (#1043)


7.0.0a6 (2020-12-18)
--------------------

New features:


- Add `sort` feature to resort all folder items [petschki] (#812)
- Remove unneeded stringtype checks [erral] (#875)
- Enable Plone 4 Control Panels: Add-ons, Dexterity Content Types [avoinea] (#984)
- Enhance traceback with ``__traceback_info__`` on import to detect the field causing the problem. [jensens] (#1009)


Bug fixes:


- Fixed deprecation warnings for ``zope.site.hooks``, ``CMFPlone.interfaces.ILanguageSchema``
  and ``plone.dexterity.utils.splitSchemaName``. [maurits] (#975)
- Update tests to fix https://github.com/plone/plone.dexterity/pull/137 [@avoinea] (#1001)
- Fix resolveuid blocks transforms [tisto, sneridagh] (#1006)
- Fix type hint example in searching documentation. [jensens] (#1008)
- Fixed compatibility with Zope 4.5.2 by making sure Location header is string.
  On Python 2 it could be unicode for the users and groups end points.
  Fixes `issue 1019 <https://github.com/plone/plone.restapi/issues/1019>`_. [maurits] (#1019)
- Check for Plone 5 in content-adding endpoint if plone.app.multilingual is installed [erral] (#1029)
- Do not test if there is a `meta_type` index. It is unused ballast. [jensens] (#2024)
- Fix tests with Products.MailHost 4.10. [maurits] (#3178)


7.0.0a5 (2020-08-21)
--------------------

New features:

- Improved blocks transformers: now we can handle generic transformers
  [cekk]
- Add generic block transformer for handle resolveuid in all blocks that have a *url* or *href* field
  [cekk]
- Add "smart fields" concept: if block has a *searchableText* field, this will be indexed in Plone
  [cekk, tiberiuichim] (#952)


7.0.0a4 (2020-05-15)
--------------------

New features:


- Replace internal links to files in blocks with a download url if the user has no edit permissions [csenger] (#930)


7.0.0a3 (2020-05-13)
--------------------

New features:


- In block text indexing, query for IBlockSearchableText named adapters to allow
  extraction from any block type. This avoids hardcoding for the 'text' block type.
  [tiberiuichim] (#917)


7.0.0a2 (2020-05-12)
--------------------

New features:


- Added ``IBlockFieldDeserializationTransformer`` and its counterpart,
  ``IBlockFieldSerializationTransformer`` concepts, use subscribers to
  convert/adjust value of blocks on serialization/deserialization, this enables
  an extensible mechanism to transform block values when saving content.

  Added an html block deserializer transformer, it will clean the
  content of the "html" block according to portal_transform x-html-safe settings.

  Added an image block deserializer transformer, it will use resolveuid mechanism
  to transform the url field to a UID of content.

  Move the resolveuid code from the dexterity field deserializer to a dedicated
  block converter adapter, using the above mechanism.
  [tiberiuichim] (#915)


7.0.0a1 (2020-05-11)
--------------------

New features:


- Resolve links in blocks to UIDs during deserialization and back to paths during
  serialization.
  [buchi,timo,cekk] (#808)


6.15.1 (2021-02-20)
-------------------

Bug fixes:


- Fixed compatibility with Zope 4.5.2 by making sure Location header is string.
  On Python 2 it could be unicode for the users and groups end points.
  Fixes `issue 1019 <https://github.com/plone/plone.restapi/issues/1019>`_.
  [maurits] (#1019)


6.15.0 (2020-10-08)
-------------------

New features:

- Add `sort` feature to resort all folder items
  [petschki] (#812)

- Remove unneeded stringtype checks
  [erral] (#875)


Bug fixes:


- Fixed deprecation warnings for ``zope.site.hooks``, ``CMFPlone.interfaces.ILanguageSchema``
  and ``plone.dexterity.utils.splitSchemaName``.
  [maurits] (#975)

- Update tests to fix https://github.com/plone/plone.dexterity/pull/137
  [@avoinea] (#1001)

- Fix tests with Products.MailHost 4.10.
  [maurits] (#3178)


6.14.0 (2020-08-28)
-------------------

New features:

- Add @types endpoint to be able to add/edit/delete CT schema [Petchesi-Iulian, avoinea] (#951)


6.13.8 (2020-08-20)
-------------------

Bug fixes:


- Removed useless management of metadata_fields in SearchHandler/LazyCatalogResultSerializer since it is handled in DefaultJSONSummarySerializer. [gbastien] (#970)


6.13.7 (2020-07-16)
-------------------

Bug fixes:


- Add a Decimal() converter
  [fulv] (#963)


6.13.6 (2020-07-09)
-------------------

Bug fixes:


- Fix Plone 5.2.x deprecation message 'ILanguageSchema is deprecated'.
  [timo] (#975)
- Do not hardcode the port in tests because it may depend on environment variables [ale-rt] (#978)


6.13.5 (2020-06-29)
-------------------

Bug fixes:


- Remove the use of plone.api in upgrade code
  [erral] (#917)


6.13.4 (2020-06-18)
-------------------

Bug fixes:


- Re-add test folder to the release (ignore the tests/images folder though). [timo] (#968)


6.13.3 (2020-06-17)
-------------------

Bug fixes:


- Take the `include_items` parameter into account in `SerializeCollectionToJson`. [gbastien] (#957)


6.13.2 (2020-06-15)
-------------------

Bug fixes:


- Include plone.app.controlpanel permissions.zcml in database service to avoid ConfigurationExecutionError regarding 'plone.app.controlpanel.Overview' permission while starting Plone 4.3.x [gbastien] (#956)


6.13.1 (2020-06-03)
-------------------

Bug fixes:


- PATCH (editing) in @user endpoint now is able to remove existing values using null
  [sneridagh] (#946)


6.13.0 (2020-05-28)
-------------------

New features:


- Expose author_image in comments endpoint [timo] (#948)


6.12.0 (2020-05-11)
-------------------

New features:


- Add database endpoint [timo] (#941)


6.11.0 (2020-05-08)
-------------------

New features:


- Add type-schema adapters for: Email, URI and Password
  [avoinea] (#926)


6.10.0 (2020-05-07)
-------------------

New features:


- Add system endpoint. [timo] (#736)


6.9.1 (2020-05-07)
------------------

Bug fixes:


- Fixed @translations endpoint to only retrieve the translations that the current user
  can really access using ``get_restricted_translations`` instead. This fixes the use
  case where an user with no permissions on a translation accessing the endpoint returned
  a 401.
  [sneridagh] (#937)


6.9.0 (2020-05-06)
------------------

New features:


- Add endpoints for managing addons. [esteele] (#733)


6.8.1 (2020-05-04)
------------------

Bug fixes:


- Treat next/prev items for unordered folders.
  [rodfersou] (#928)


6.8.0 (2020-04-23)
------------------

New features:


- Managing Dexterity Type Creation (CRUD) via plone.restapi
  [avoinea] (#534)


6.7.0 (2020-04-21)
------------------

New features:


- Make @querystring-search endpoint context aware
  [sneridagh] (#911)


Bug fixes:


- Fix sphinxbuilder with Python 3.8
  [avoinea] (#905)


6.6.1 (2020-04-17)
------------------

Bug fixes:


- call unescape method on received html for richtext before save it in Plone.
  [cekk] (#913)
- Small fix in IBlocks test, addedd a missing assert call
  [tiberiuichim] (#914)


6.6.0 (2020-04-07)
------------------

New features:


- Add next_item and previous_item attributes to allow to navigate to the previous and next sibling in the container the document is located.
  [rodfersou] (#900)


6.5.2 (2020-04-01)
------------------

Bug fixes:


- Fix for the use case while updating user properties in the @user endpoint, and the
  portrait is already previously set but the request includes the (previously) serialized
  value as a string because the user are not updating it
  [sneridagh] (#896)


6.5.1 (2020-04-01)
------------------

Bug fixes:


- Fix deleting user portrait.
  [buchi] (#751)


6.5.0 (2020-03-30)
------------------

New features:


- Link translation on content creation feature and new @translation-locator endpoint
  [sneridagh] (#887)


6.4.1 (2020-03-25)
------------------

Bug fixes:


- Make discussion endpoint return content that is deserialized via portal transforms (e.g. 'text/x-web-intelligent') [timo] (#889)


6.4.0 (2020-03-23)
------------------

New features:


- Add targetUrl to the dxcontent serializer for primary file fields to be able to download a file directly.
  [csenger] (#886)


Bug fixes:


- Fixed package install error with Python 3.6 without locale.
  See `coredev issue 642 <https://github.com/plone/buildout.coredev/issues/642#issuecomment-597008272>`_.
  [maurits] (#642)
- plone.app.discussion extends the review workflow for moderation of comments. This change takes the additional workflow states into account.
  [ksuess] (#842)


6.3.0 (2020-03-03)
------------------

New features:


- Allow using object paths and UIDs to link translations
  [erral] (#645)


Bug fixes:


- Add a catalog serializer guard when returning fullobjects in case the object doesn't
  exist anymore because for some reason it failed to uncatalog itself.
  [sneridagh] (#877)
- Use longer password in tests.  [maurits] (#3044)


6.2.4 (2020-02-20)
------------------

Bug fixes:


- fullobjects qs is missing in response batch links in batching operations
  [sneridagh] (#868)


6.2.3 (2020-02-19)
------------------

Bug fixes:


- Return proper None instead of string "None" on the choice schema serializer [sneridagh] (#863)


6.2.2 (2020-01-24)
------------------

Bug fixes:


- Degrade gracefully when a term set in a content field does not exists in the assigned vocabulary [sneridagh] (#856)


6.2.1 (2020-01-22)
------------------

Bug fixes:


- Sharing POST: Limit roles to ones the user is allowed to delegate.
  [lgraf] (#857)


6.2.0 (2020-01-10)
------------------

New features:


- Make ?fullobjects work in AT Collections to get the full JSON representation of the items
  [erral] (#698)
- Make ?fullobjects work in Dexterity Collections to get the full JSON representation of the items
  [erral] (#848)


Bug fixes:


- Fix WorkflowException for related items with no review_state.
  [arsenico13] (#376)


6.1.0 (2020-01-05)
------------------

New features:


- Add SearchableText indexing for text in blocks
  [luca-bellenghi] (#844)


6.0.0 (2019-12-22)
------------------

Breaking changes:


- Remove IAPIRequest marker interface from plone.restapi. The correct interface should be imported from plone.rest.interfaces instead. If anybody was using this marker Interface, it didn't do anything. (#819)


Bug fixes:


- Prevent converting bytestring ids to unicode ids when reordering (see upgrade guide for potential migration).
  [deiferni] (#827)


5.1.0 (2019-12-07)
------------------

New features:


- Add Python 3.8 support @timo (#829)


5.0.3 (2019-12-06)
------------------

Bug fixes:


- Change to use the short name for the Blocks behavior instead of using the interface one. It fixes #838.
  [sneridagh] (#838)


5.0.2 (2019-11-06)
------------------

Bug fixes:


- Fix filtering vocabs and sources by title with non-ASCII characters.
  [lgraf] (#825)


5.0.1 (2019-11-05)
------------------

Bug fixes:


- Fix serialization of vocabulary items for fields that need hashable items (e.g. sets).
  [buchi] (#788)


5.0.0 (2019-10-31)
------------------

Breaking changes:


- Rename tiles behavior and fields to blocks, migration step.
  [timo, sneridagh] (#821)


Bug fixes:


- Fixed startup error when Archetypes is there, but ``plone.app.blob`` or ``plone.app.collection`` not.
  [maurits] (#690)


4.6.0 (2019-10-06)
------------------

New features:


- Add @sources and @querysources endpoints, and link to them from JSON schema in @types response.
  [lgraf] (#790)


Bug fixes:


- Explicitly load zcml of dependencies, instead of using ``includeDependencies``
  [maurits] (#2952)


4.5.1 (2019-09-23)
------------------

Bug fixes:


- Fire ModifiedEvent when field is set to null in a PATCH request.
  [phgross] (#802)

- Testing: Drop freezegun and instead selectively patch some timestamp accessors.
  [lgraf] (#803)


4.5.0 (2019-09-12)
------------------

New features:


- Add @querystring-search endpoint that returns the results of a search using a p.a.querystring query.
  [sneridagh] (#789)
- Use Plone 5.2 and Python 3 as default to generate documentation. [timo] (#800)


Bug fixes:


- Make group serializer results predictable by returning sorted item results. [timo] (#798)


4.4.0 (2019-08-30)
------------------

New features:


- Add @querystring endpoint that dumps p.a.querystring config.
  [lgraf] (#754)


Bug fixes:


- Fix typo in the ``tiles_layout`` field title name.
  [sneridagh] (#785)


4.3.1 (2019-07-10)
------------------

Bug fixes:


- Fix @sharing POST when called on the plone site root
  [csenger] (#780)


4.3.0 (2019-06-30)
------------------

New features:


- Support retrieval of additional metadata fields in summaries in the same way as
  in search results.
  [buchi] (#681)


4.2.0 (2019-06-29)
------------------

New features:


- Make @types endpoint expandable.
  [lgraf] (#766)
- Factor out permission checks in @users endpoint
  to make it more easily customizable.
  [lgraf] (#771)


Bug fixes:


- Gracefully handle corrupt images when serializing scales.
  [lgraf] (#729)
- Docs: Make sure application/json+schema examples also get syntax highlighted.
  [lgraf] (#764)
- Return empty response for status 204 (No Content).
  [buchi] (#775)
- Return status 400 if a referenced object can not be resolved during deserialization.
  [lgraf] (#777)


4.1.4 (2019-06-21)
------------------

Bug fixes:


- Set effective_date and reindex obj on workflow transitions. [wkbkhard] (#760)


4.1.3 (2019-06-21)
------------------

Bug fixes:


- Improve documentation for how to set relations by adding some examples.
  [buchi] (#732)
- Return an error message if a referenced object can not be resolved.
  [buchi] (#738)


4.1.2 (2019-06-15)
------------------

Bug fixes:


- @types endpoint: Fix support for context aware default factories.
  [lgraf] (#748)


4.1.1 (2019-06-13)
------------------

Bug fixes:


- Handle ``None`` as a vocabulary term title in the vocabulary serializer.
  [Rotonen] (#742)
- Handle a term not having a title attribute in the vocabulary serializer.
  [Rotonen] (#742)
- Handle a term having a non-ASCII ``str`` title attribute in the vocabulary
  serializer.
  [Rotonen] (#743)
- Fix time freezing in Plone 5.1 tests.
  [lgraf] (#745)


4.1.0 (2019-05-25)
------------------

New features:

- Use Black on the code base. [timo] (#693)


4.0.0 (2019-05-09)
------------------

Breaking changes:

- @vocabularies service: No longer returns an @id for terms. Results are batched, and terms are now listed as items instead of terms to match other batched responses. Batch size is 25 by default but can be overridden using the b_size parameter.
  [davisagli]

- @types service: Choice fields using named vocabularies are now serialized with a vocabulary property giving the URL of the @vocabularies endpoint for the vocabulary instead of including choices, enum and enumNames inline. The subjects field is now serialized as an array of string items using the plone.app.vocabularies.Keywords vocabulary.
  [davisagli]

- Serialize widget parameters into a widgetOptions object instead of adding them to the top level of the schema property.
  [davisagli]

- Add `title` and `token` filter to the vocabularies endpoint.
  [davisagli, sneridagh, timo] (#535)

- Use tokens for serialization/deserialization of vocabulary terms.
  [buchi] (#691)

- Return the token and the title of vocabulary terms in serialization.
  See upgrade guide for more information.
  [buchi] (#726)

New Features:

- ``@vocabularies`` service: Use ``title`` parameter to filter terms by title
  and ``token`` for getting the title of a term given a token.
  (case-insensitive).
  [davisagli, sneridagh, timo]

Bug fixes:

- Standardize errors data structure of email-notification endpoint.
  [cekk] (#708)

- When renewing an expired or invalid authentication token with ``@login-renew`` fail with a ``401`` error instead of returning a new authentication token.
  [thet] (#721)

- Use interface name in the ``tiles`` profile instead of the shorthand behavior name. This fixes #724.
  [sneridagh] (#724)

- Avoid calculating batch links for catalog results twice.
  [davisagli]


3.9.0 (2019-04-18)
------------------

New features:

- Add full support for `fullobjects` support for AT content types.
  [sneridagh] (#698)


3.8.1 (2019-03-21)
------------------

Bug fixes:

- Fixed Python 3 incompatiblity with workflow service (#676)
  [ajung]

- Hide performance, testing, and tiles profile. (#700)
  [timo]


3.8.0 (2019-03-21)
------------------

New features:

- Add support for add/update user portraits (@user endpoint)
  [sneridagh] (#701)


3.7.5 (2019-03-14)
------------------

Bug fixes:

- Do not depend on the deprecated plone.app.controlpanel package.
  [sneridagh] (#696)


3.7.4 (2019-03-13)
------------------

Bug fixes:

- Fix a problem on ZCML loading depending on how the policy package is named,
  related to the load of permissions in control panels and multilingual.
  [sneridagh] (#526)


3.7.3 (2019-03-08)
------------------

Bug fixes:

- Use environment-markers instead of python-logic to specify dependencies for py2.
  [pbauer] (#688)


3.7.2 (2019-03-07)
------------------

Bug fixes:

- Fix TUS upload events `#689 <https://github.com/plone/plone.restapi/issues/689>`_.
  [buchi] (#689)


3.7.1 (2019-03-06)
------------------

Bugfixes:

- Fix release to not create universal (Python 2/3) wheels.
  [gforcada]

- Install zestreleaser.towncrier in the buildout to the changelog is updated correctly. (#684)
  [maurits]


3.7.0 (2019-03-04)
------------------

New Features:

- Add group roles to @groups serializer
  [sneridagh]


3.6.0 (2019-02-16)
------------------

New Features:

- Enhance site root to serialize and deserialize 'tiles' and 'tiles_layout' attributes.
  [sneridagh]

- Fix @workflow endpoint on site root to return an empty object instead of a 404.
  [sneridagh]


3.5.2 (2019-02-14)
------------------

Bugfixes:

- Fix serializing the Event type. This fixes https://github.com/plone/plone.restapi/issues/664.
  [davisagli, elioschmutz]


3.5.1 (2019-02-05)
------------------

Bugfixes:

- Do not fail on serializing types with fields having non-parametrized widgets.
  Fixes issue `664 <https://github.com/plone/plone.restapi/issues/664>`_.
  [elioschmutz]


3.5.0 (2018-11-06)
------------------

New Features:

- Add Python 3 support.
  [pbauer, davisagli]


3.4.5 (2018-09-14)
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
