Sharing
=======

Plone comes with a sophisticated user management system that allows to assign users and groups with global roles and permissions. Sometimes this in not enough though and you might want to give users the permission to access or edit a specific part of your website or a specific content object. This is where local roles (located in the Plone sharing tab) come in handy.


Retrieve Local Roles
--------------------

In plone.restapi, the representation of any content object will include a hypermedia link to the local role / sharing information in the 'sharing' attribute:

.. code:: json

  GET /plone/folder
  Accept: application/json

  HTTP 200 OK
  content-type: application/json

  {
    "@id": "http://localhost:55001/plone/folder",
    "@type": "Folder",
    ...
    "sharing": {
      "@id": "http://localhost:55001/plone/folder/@sharing",
      "title": "Sharing",
    }
  }

RFC: Do we care about those hypermedia links on the top level for better discoverability?

The sharing information of a content object can also be directly accessed by appending '/@sharing' to the GET request to the URL of a content object. E.g. to access the sharing information for a top-level folder, do:

.. code:: json

  GET /plone/folder/@sharing
  Accept: application/json

  HTTP 200 OK
  content-type: application/json

  {
     "inherit" : false,
     "entries" : [
        {
           "disabled" : false,
           "title" : "Logged-in users",
           "id" : "AuthenticatedUsers",
           "login" : null,
           "type" : "group",
           "roles" : {
              "Reader" : false,
              "Editor" : false,
              "Contributor" : false,
              "Reviewer" : false
           }
        },
        {
           "id" : "test_user_1_",
           "title" : "test-user",
           "disabled" : false,
           "roles" : {
              "Reviewer" : true,
              "Contributor" : false,
              "Editor" : false,
              "Reader" : false
           },
           "type" : "user"
        }
     ]
  }
  

RFC: We can not return a full list of all users and groups in the portal here. This would not scale for portals with lots of users. We could always list the local roles that are available. It is fair to assume that the number of local roles is somehow limited.


Update Local Roles
------------------

You can update the 'sharing' information by sending a POST request to the object URL and appending '/@sharing', e.g. '/plone/folder/@sharing'. E.g. say you want to give the AuthenticatedUsers group the 'reader' local role for a folder:

.. code:: json

  POST /plone/folder/@sharing
  Host: localhost:8080
  Accept: application/json
  Content-Type: application/json

  {
     "inherit" : true,
     "entries" : [
        {
           "id" : "test_user_1_",
           "roles" : {
              "Reviewer" : true,
              "Editor" : false,
              "Reader" : true,
              "Contributor" : false
           },
           "type" : "user"
        }
     ]
  }
  

RFC: I'm wondering if a POST request is the correct HTTP verb. We are actually updating an object, which would make PATCH a more appropriate choice. Though, we are not embedding the sharing information in the standard view (something that could also be a possible option.)
