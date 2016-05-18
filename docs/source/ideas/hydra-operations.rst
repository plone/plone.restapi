Resource Operations
-------------------

"Hydra has three predefined operation classes, namely CreateResourceOperation, ReplaceResourceOperation, and DeleteResourceOperation. As their names suggest, they can be used to implement simple CRUD functionality. More specialized operations can be easily created by subclassing these classes or their base class Operation." -- http://www.w3.org/ns/hydra/spec/latest/core/

"An Operation represents the information necessary for a client to construct valid HTTP requests in order to manipulate the server's resource state." -- http://www.w3.org/ns/hydra/spec/latest/core/

Operations on a Folder::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/"
    "@type": "Folder",
    "operation": [
        {
            "@type": "CreateResourceOperation",
            "name": "Create Resource",
            "method": "POST",
            "expects": {
                "supportedProperty": [
                    {
                        "@type": "PropertyValueSpecification",
                        "hydra:property": "@type",
                        "hydra:required": "true",
                        "readOnlyValue": "false"
                    },
                    {
                        "@type": "PropertyValueSpecification",
                        "hydra:property": "title",
                        "hydra:required": "true",
                        "readOnlyValue": "false"
                    },
                ],
            }
        },
        {
            "@type": "ReplaceResourceOperation",
            "name": "Update Resource",
            "method": "PATCH",
            "expects": {
                "supportedProperty": [
                    {
                        "@type": "PropertyValueSpecification",
                        "hydra:property": "@type",
                        "hydra:required": "false",
                        "readOnlyValue": "false"
                    },
                    {
                        "@type": "PropertyValueSpecification",
                        "hydra:property": "title",
                        "hydra:required": "false",
                        "readOnlyValue": "false"
                    },
                    ...
                ],
            }
        },
        {
            "@type": "DeleteResourceOperation",
            "name": "Delete Resource",
            "method": "DELETE",
        }
    ]
  }


Operations on a Document::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/"
    "@type": "Document",
    "operation": [
      {
        "@type": "ReplaceResourceOperation",
        "name": "Update Resource",
        "method": "PATCH",
      },
      {
        "@type": "DeleteResourceOperation",
        "method": "DELETE"
      }
    ]
  }
