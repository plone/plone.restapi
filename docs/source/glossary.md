---
myst:
  html_meta:
    "description": "plone.restapi Glossary"
    "property=og:description": "plone.restapi Glossary"
    "property=og:title": "Glossary"
    "keywords": "Plone, plone.restapi, REST, API, Glossary"
---

# Glossary

```{glossary}
:sorted: true

REST
    REST stands for [Representational State Transfer](https://en.wikipedia.org/wiki/Representational_state_transfer). It is a software architectural principle to create loosely coupled web APIs.

workflow
    A concept in Plone (and other CMS's) whereby a content object can be in a number of states (private, public, etcetera) and uses transitions to change between them (e.g. "publish", "approve", "reject", "retract"). See the [Plone docs on Workflow](https://5.docs.plone.org/working-with-content/collaboration-and-workflow/)

HTTP-Request
HTTP Request
Request
Requests
    The initial action performed by a web client to communicate with a server. The {term}`Request` is usually followed by a {term}`Response` by the server, either synchronous or asynchronous (which is more complex to handle on the user side)

HTTP-Response
HTTP Response
Response
    Answer of or action by the server that is executed or send to the client after the {term}`Request` is processed.

HTTP-Header
HTTP Header
Header
    The part of the communication of the client with the server that provides the initialisation of the communication of a {term}`Request`.

HTTP-Verb
HTTP Verb
Verb
    One of the basic actions that can be requested to be executed by the server (on an object) based on the {term}`Request`.

Object URL
    The target object of the {term}`Request`

Authorization Header
    Part of the {term}`Request` that is responsible for the authentication related to the right user or service to ask for a {term}`Response`.

Accept Header
    Part of the {term}`Request` that is responsible to define the expected type of data to be accepted by the client in the {term}`Response`.

Authentication Method
    Access restriction provided by the connection chain to the server exposed to the client.

Basic Auth
    A simple {term}`Authentication Method` referenced in the {term}`Authorization Header` that needs to be provided by the server.

content rule
    A content rule will automatically perform an action when a certain event, known as a {term}`trigger`, takes place.

trigger
    A trigger is an event in Plone that causes the execution of defined actions.
    Example triggers include object modified, user logged in, and workflow state changed.
```
