# Threat model for plone.restapi (guidance for OSS Scanner)

> Maintainers: review every statement below before merging. Items marked **(confirm)** are my best understanding and should be checked against the project's actual behaviour and the Plone Security Team's policies.

## What this project is

`plone.restapi` is a Python add-on for the Plone CMS (built on Zope) that exposes a JSON/REST API: content CRUD (GET/POST/PATCH/DELETE on content URLs, reached via `++api++` or `Accept: application/json`), authentication, search, users/groups/roles, workflow, schema/types, vocabularies, registry and controlpanels, uploads (including TUS), copy/move, history, comments, navigation, add-on management, email sending, and many other `@`-prefixed endpoints ("services"). It is the backend of the Volto frontend and is used directly by third-party clients.

## Security model

Plone does not have one static authorization policy for each broad class of caller. Its security model combines named permissions, roles, and contextual checks. Roles are assigned to users and groups; permissions are assigned to roles and checked against the object or service context. Assignments may be global, local to content, inherited through the content hierarchy, or defined by a workflow state. Code also protects individual methods and operations with security declarations, decorators, and explicit calls such as `checkPermission`. The effective result therefore depends on the deployed packages and profiles, site configuration, current user and groups, target object, and its workflow state. Assess an API operation against the permission checks and equivalent Plone operation for that same user and context, rather than assuming a fixed Member/Editor/Administrator capability table.

Permission and role defaults are distributed across Zope and Plone packages: Zope's [`AccessControl`](https://github.com/zopefoundation/AccessControl) supplies security declarations and permission checks; Plone and its add-ons register permissions and assign them in ZCML or GenericSetup profiles, and site administrators can further configure assignments. Concrete Plone defaults are defined in [`Products.CMFPlone`'s rolemap.xml](https://github.com/plone/Products.CMFPlone/blob/master/src/Products/CMFPlone/profiles/default/rolemap.xml) and its [default workflow definitions](https://github.com/plone/Products.CMFPlone/tree/master/src/Products/CMFPlone/profiles/default/workflows); Plone permission names are exposed in [`plone.base.permissions`](https://github.com/plone/plone.base/blob/main/src/plone/base/permissions.py). For example, this package grants `plone.restapi: Use REST API` to `Anonymous` in its [upgrade rolemap](../src/plone/restapi/upgrades/profiles/0002/rolemap.xml), while its [authentication documentation](../docs/source/usage/authentication.md#permissions) explains that individual services also need permissions such as `View` for reads and `Add portal content` for creation. The [sharing documentation](../docs/source/endpoints/sharing.md) demonstrates assigning a local role to a group on a particular folder, and the [workflow documentation](../docs/source/endpoints/workflow.md) describes state transitions. As a higher-privilege example, control-panel and system operations are guarded by permissions such as `Manage Portal` or the Plone control-panel overview permission; the [system endpoint docs](../docs/source/endpoints/system.md) describe that gate. The [group creation service](../src/plone/restapi/services/groups/add.py) separately prevents callers without Manager-level `Manage Portal` permission from assigning the `Manager` role.

`Manager` is a role, not a synonym for every administrator concept. Its effective capabilities still come from the installed role/permission assignments and checks. Plone also has a distinct `Site Administrator` role; do not assume the two have identical permissions or that either role implies arbitrary Python execution or filesystem access. Their assignments are defined by the Plone/Zope packages and the site's configuration, not by this API alone. In particular, a finding is in scope when the API gives a lower-privilege caller a capability that the corresponding Plone operation would deny; Manager-authorized site administration is not, by itself, a vulnerability under this model.

Workflows are an intended dynamic security mechanism, not an exception to the model. A workflow can change a content object's state and thereby change permissions on that object; transitions themselves have guards, and workflow mappings may differ by content type or site configuration. Evaluate access to content and transitions in the object's current state, and check that changing state or traversing a transition cannot expose or mutate content beyond the caller's authority. See Plone's [workflow documentation](https://6.docs.plone.org/backend/workflows.html) and this package's [workflow endpoint docs](../docs/source/endpoints/workflow.md).

Plone is also not a flat URL-to-record API. It is built on a hierarchical object tree: URL traversal resolves containers, content, views, and REST service traversers; Zope acquisition can make parent attributes and tools available in a child context. This affects which object a check must use and which permissions or roles are inherited. Request traversal and `restrictedTraverse` apply security checks; `unrestrictedTraverse` bypasses them and requires the calling code to enforce access appropriately. See the Plone docs on [traversal and acquisition](https://6.docs.plone.org/backend/traversal-acquisition.html) and the [Zope object-publishing](https://zope.readthedocs.io/en/latest/zdgbook/ObjectPublishing.html) and [acquisition](https://zope.readthedocs.io/en/latest/zdgbook/Acquisition.html) references.

`plone.protect` addresses request-forgery protections for browser-driven writes (including CSRF tokens and POST-only guards); it is not an authorization system and does not replace permission checks. Some REST API mutation handlers explicitly opt out of its automatic CSRF protection, so review those paths together with their authentication method, permission checks, and browser/CORS assumptions. Separately, `RestrictedPython` constrains code used in restricted through-the-web contexts; it is not a general sandbox and does not make arbitrary request data or the REST API's installed Python code safe. See Plone's [CSRF documentation](https://6.docs.plone.org/classic-ui/csrf.html) and [RestrictedPython security considerations](https://restrictedpython.readthedocs.io/en/latest/usage/security_considerations.html).

## Trust boundaries and untrusted input

Everything in an HTTP request is untrusted: URL path and traversal segments, query strings, headers, JSON bodies, uploaded file contents, TUS upload metadata, and values in content fields, blocks and registry records. Key entry points:

1. **Authentication** (`@login`, `@login-renew`, `@logout`, JWT token plugin, password reset / `@users` registration endpoints). Concerns: token forgery or replay, signature/expiry bypass, user enumeration beyond intended behaviour, password-reset token weaknesses, brute-force protection gaps, privilege escalation via crafted tokens.
2. **Deserialization** (JSON → field values and blocks). Concerns: setting fields or attributes the user lacks permission to write, mass-assignment of internal attributes, type confusion, unsafe resolution of references (`resolveuid`, relations, UID/path lookups) that bypass access checks.
3. **Serialization / expansion** (content, `expand=`, `@search`, `@querystring-search`, `@navigation`, `@breadcrumbs`, `@vocabularies`, `@sources`, `@relations`, `@history`, `@comments`). Concerns: information disclosure of content, fields, workflow state, user data or private metadata the caller may not View; leaking restricted objects through expansions, batching, catalog results or error messages.
4. **Users, groups, roles, principals endpoints** (`@users`, `@groups`, `@roles`, `@principals`, `@role-assignments`/local roles). Concerns: any path allowing a non-privileged caller to read other users' private properties, create/modify users, change passwords, or grant roles.
5. **Write operations with side effects** (copy/move, workflow transitions, lock/unlock, content-rules, add-on install/uninstall, registry and control panel updates, email sending, database/system information). Concerns: missing permission checks, checks on the wrong object (source vs target), CSRF-like or confused-deputy issues, SSRF, mail header injection or abuse as an open relay.
6. **File and upload handling** (file/image fields, TUS uploads, `@upload`). Concerns: path traversal, unbounded resource consumption, content-type confusion leading to stored XSS when served, unsafe temporary file handling.
7. **Traversal** (`++api++`, `++resource++`, namespace traversers, service lookup by name). Concerns: reaching unintended views/adapters, bypassing permission declarations, unauthorized access to private attributes via traversal.
8. **Query construction** (catalog query building from query strings and JSON bodies). Concerns: queries returning unauthorized results, denial of service via pathological queries.

## What is in scope (please report)

- Authentication or authorization bypass; privilege escalation.
- Reading or modifying content or data the caller lacks permission for.
- Remote code execution, arbitrary file read/write, SSRF, XXE, unsafe deserialization (pickle/eval/exec of request data).
- Stored or reflected XSS that is exploitable through content served by the API or by clients that render API output as documented.
- Information disclosure of credentials, tokens, secrets or other users private data.
- Denial of service from a small unauthenticated or low-privilege request (algorithmic complexity, unbounded memory/disk, unbounded recursion).

## Out of scope / not a vulnerability by itself

- Actions requiring Manager (or equivalent) rights that Plone already allows Managers to perform (e.g. changing site configuration, installing add-ons). Report only if the API grants such power to a lower role.
- Issues that exist only in Plone core, Zope, or other dependencies and are not reachable or worsened through plone.restap (report upstream: Products.CMFPlone / Zope).
- Findings only reproducible with debug flags, test-only layers, demo fixtures, or intentionally insecure test configuration.
- Missing rate limiting / brute-force protection at the application layer where deployment (proxy/WAF) is expected to handle it.
- Content that is intentionally public (anonymous View on published content).

## Severity guidance

- **Critical**: unauthenticated RCE; unauthenticated authentication bypass or admin takeover; unauthenticated arbitrary file read/write.
- **High**: authenticated low-privilege user gains Manager/Site Administrator or RCE; any user reads or modifies content/data clearly beyond their permissions on a default site (including private content or other users' credentials/tokens); stored XSS executed in an admin context via API data.
- **Medium**: limited information disclosure (non-sensitive metadata or user enumeration beyond the intended); authorization checks missing on low-impact operations; DoS requiring authentication; reflected XSS needing user interaction.
- **Low**: hardening gaps, verbose errors, issues requiring unlikely configuration or pre-existing high privileges.

## Reproducers and patches

- Provide a reproducer using the project's test layers (`plone.restapi.testing`, e.g. `PLONE_RESTAPI_DX_FUNCTIONAL_TESTING`) or HTTP requests against a default Plone 6 site with the relevant user role, stating exactly which role is used for each request.
- State which permission or role the attacker holds and which the operation should require.
- Proposed patches should be minimal, follow existing code style, include a regression test, and add a changelog entry in `news/` (towncrier fragment). Prefer fixing the permission check or serializer/deserializer at the root rather than adding endpoint-specific filters.
- The patch should be compatible with Python 3.8 as minimum.  This could be tested with the `py38-plone52` tox environment, but that would require network access.
