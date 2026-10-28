# Threat model for plone.restapi (guidance for OSS Scanner)

> Maintainers: review every statement below before merging. Items marked **(confirm)** are my best understanding and should be checked against the project's actual behaviour and the Plone Security Team's policies.

## What this project is

`plone.restapi` is a Python add-on for the Plone CMS (built on Zope) that exposes a JSON/REST API: content CRUD (GET/POST/PATCH/DELETE on content URLs, reached via `++api++` or `Accept: application/json`), authentication, search, users/groups/roles, workflow, schema/types, vocabularies, registry and controlpanels, uploads (including TUS), copy/move, history, comments, navigation, add-on management, email sending, and many other `@`-prefixed endpoints ("services"). It is the backend of the Volto frontend and is used directly by third-party clients.

## Security model

Plone's authorization is permission-based (Zope security declarations, roles, local roles, workflow-state permissions). The API must never allow more than the equivalent UI/Python operation would for the same user.

Principals:

- **Anonymous**: can reach only what Plone permissions grant (typically View on published content). Network-reachable, fully untrusted.
- **Authenticated users** (Member, Contributor, Editor, Reviewer, etc.): untrusted with respect to other users and to server resources. They must not exceed their permissions on any object.
- **Site Administrator / Manager**: trusted to administer the site. They are not expected to be sandboxed from site configuration, but should not gain arbitrary code execution or filesystem access through the API unless Plone already grants that to them.

## Trust boundaries and untrusted input

Everything in an HTTP request is untrusted: URL path and traversal segments, query strings, headers, JSON bodies, uploaded file contents, TUS upload metadata, and values in content fields, blocks and registry records. Key entry points:

1. **Authentication** (`@login`, `@login-renew`, `@logout`, JWT token plugin, password reset / `@users` registration endpoints). Concerns: token forgery or replay, signature/expiry bypass, user enumeration beyond intended behaviour, password-reset token weaknesses, brute-force protection gaps, privilege escalation via crafted tokens.
2. **Deserialization** (JSON → field values and blocks). Concerns: setting fields or attributes the user lacks permission to write, mass-assignment of internal attributes, type confusion, unsafe resolution of references (`resolveuid`, relations, UID/path lookups) that bypass access checks.
3. **Serialization / expansion** (content, `expand=`, `@search`, `@querystring-search`, `@navigation`, `@breadcrumbs`, `@vocabularies`, `@sources`, `@relations`, `@history`, `@comments`). Concerns: information disclosure of content, fields, workflow state, user data or private metadata the caller may not View; leaking restricted objects through expansions, batching, catalog results or error messages.
4. **Users, groups, roles, principals endpoints** (`@users`, `@groups`, `@roles`, `@principals`, `@role-assignments`/local roles). Concerns: any path allowing a non-privileged caller to read other users' privateproperties, create/modify users, change passwords, or grant roles.
5. **Write operations with side effects** (copy/move, workflow transitions, lock/unlock, content-rules, add-on install/uninstall, registry and control panel updates, email sending, database/system information). Concerns: missing permission checks, checks on the wrong object (source vs target), CSRF-like or confused-deputy issues, SSRF, mail header injection or abuse as an open relay.
6. **File and upload handling** (file/image fields, TUS uploads, `@upload`). Concerns: path traversal, unbounded resource consumption, content-type confusion leading to stored XSS when served, unsafe temporary file handling.
7. **Traversal** (`++api++`, `++resource++`, namespace traversers, service lookup by name). Concerns: reaching unintended views/adapters, bypassing permission declarations, unauthorized access to private attributes via traversal.
8. **Query construction** (catalog query building from query strings and JSON bodies). Concerns: queries returning unauthorized results, denial of service via pathological queries; note that ZCatalog is not SQL, so classic SQL injection does not apply.

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
