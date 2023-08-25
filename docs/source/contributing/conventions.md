---
myst:
  html_meta:
    "description": "Naming convention for REST API resources and endpoints."
    "property=og:description": "Naming convention for REST API resources and endpoints."
    "property=og:title": "Conventions"
    "keywords": "Plone, plone.restapi, REST, API, Conventions"
---

# Conventions


## Naming Convention for REST API Resources and Endpoints


### Nouns versus Verbs

**Rule:** Use nouns to represent resources.

**Do:**

```text
/my-folder
/@registry
/@types
```

**Don't:**

```text
/createFolder
/deleteDocument
/updateEvent
```

**Reason:**

RESTful URIs should refer to a resource that is a thing (noun) instead of referring to an action (verb).
Nouns have properties, whereas verbs do not.
The REST architectural principle uses HTTP verbs to interact with resources.

There is an exception to that rule.
Verbs can be used for specific actions or calculations, for example:

```text
/login
/logout
/move-to
/reset-password
```

### Singular versus Plural

**Rule:** Use plural resources.

**Do:**

```text
/users
/users/21
```

**Don't:**

```text
/user
/user/21
```

**Reason:**

If you use singular for a collection-like resource—such as `/user` to retrieve a list of all users—it feels wrong.
Mixing singular and plural is confusing.
For example, using `/users` for retrieving users, and `/user/21` to retrieve a single user.


### URL Parameters (singular vs plural)

**Rule:** Use plural for URL parameters that can contain one or multiple items. Use singular for parameters that can contain only one single item.

**Do:**

If the parameter allows passing multiple values:

```text
/tokens
```

If the parameter allows passing a single value only:

```text
/token
```

**Don't:**

If the parameter allows passing multiple values, do not use the singular form, and do not append a type to the variable name. The following are examples of what _not_ to do:

```text
/token
/token_list
/token_array
/token_set
```

**Reason:**

The naming should clearly indicate if an attribute expects a single (singular) item or multiple items (plural).
We decided to use the plural form, instead of appending a possible type—such as `_list`, `_array`, or `_set`—to the variable name.

See https://github.com/plone/plone.restapi/pull/1295#issuecomment-997281715 for the discussion that led to this decision.

### Uppercase versus Lowercase

**Rule:** Use lowercase letters in URIs.

**Do:**

```text
https://example.com/my-folder/my-document
```

**Don't:**

```text
https://example.com/My-Folder/My-Document
```

**Reason:** RFC 3986 defines URIs as case-sensitive except for the scheme and host components.

Those two URIs are equivalent:

```text
https://example.org/my-folder/my-document
HTTPS://EXAMPLE.ORG/my-folder/my-document
```

While this one is not equivalent to the two URIs above:

```text
https://example.org/My-Folder/my-document
```

To avoid confusion we always use lowercase letters in URIs.


## Naming Convention for attribute names in URIs

**Rule:** Use hyphens (spinal case) to improve readability of URIs.

**Do:**

```text
/users/noam/reset-password
```

**Don't:**

```text
/users/noam/resetPassword
/users/noam/ResetPassword
/users/noam/reset_password
```

**Reason:**

Spinal case is easier to read and safer to use than camelCase.
URLs are case-sensitive (RFC3986).
Plone uses spinal case for URL creation.
The page title "My page" becomes "my-page".
Mixed naming conventions in URLs would be confusing.
For example, `/my-folder/@send_url_to_user`, is confusing.
[Google recommends spinal-case in URLs](https://developers.google.com/search/docs/crawling-indexing/url-structure) for better search engine optimization.

**Discussion:**

<https://github.com/plone/plone.restapi/issues/194>


## Naming Convention for attribute names in response body

**Rule:** Use snake_case to reflect Python best practices.

**Do:**

```text
{
  translation_of: ...
}
```

**Don't:**

```text
{
  translationOf: ...,
  TranslationOf: ...,
}
```

**Reason:**

We map over Python attributes one-to-one whether they are snake case (modern Python and Plone, and Dexterity) or lowerCamelCase (Zope 2, Archetypes).


## Versioning

Versioning APIs makes a lot of sense for public API services.
This is especially true when an API provider needs to ship different versions of the API at the same time.
Plone already has a way to version packages.
It currently does not make sense for us to expose that information via the API.
We will always just ship one version of the API at a time.
We are usually in full control over the backend and the frontend.
