Upgrade Guide
=============

1.0b1 (unreleased)
------------------

Breaking Changes:

- Rename 'url' attribute on navigation / breadcrumb to '@id'.
  [timo]


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


1.0a17 (2017-05-31)
-------------------

Breaking Changes:

- Change RichText field value to use 'output' instead of 'raw' to fix inline
  paths. This fixes #302.
  [erral]
