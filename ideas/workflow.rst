.. include:: /alert-noindex.rst

########
Workflow
########

.. note::
   Currently the workflow support is limited to executing transitions on content.

In Plone, content almost always has a workflow attached.

The API offers the ability to change the workflow statuses of content: we already saw a hint previosuly where a content representation exposed the ``@actions`` information::

  ...
      "@actions": {
        "workflow": {
          "@href": "http://nohost/++api++1/front-page/++actions++workflow/",
          "@template": {
             "type": {
               "@type": "string",
               "@choices": [
                  "retract",
                  "reject"
               ]
             }
          }
        }
      },
  ...

Now, if we want to make the front page private, we would proceed by issuing a ``POST`` request to the given URL::

  POST /++api++1/front-page/++actions++workflow/ HTTP/1.1
  Host: nohost
  Content-Type: application/json

  {
    "type": "retract"
  }


  200 OK HTTP/1.1
  Content-Type: application/json

  {
    "@response": {
       "@href": "http://nohost/++api++1/front-page",
       "@info": {
         "review_state": "private"
       },
       "@actions": {
         "workflow": {
           "@href": "http://nohost/++api++1/front-page/++actions++workflow/",
           "@template": {
              "type": {
                "@type": "string",
                "@choices": [
                   "submit",
                   "publish"
                ]
              }
           }
         }
       }
    }
  }
