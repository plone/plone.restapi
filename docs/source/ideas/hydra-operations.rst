Resource Operations
-------------------

"Hydra has three predefined operation classes, namely CreateResourceOperation, ReplaceResourceOperation, and DeleteResourceOperation. As their names suggest, they can be used to implement simple CRUD functionality. More specialized operations can be easily created by subclassing these classes or their base class Operation." -- http://www.w3.org/ns/hydra/spec/latest/core/

DeleteResourceOperation on a Plone document::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/"
    "@type": "Collection",
    "operation": [
      {
        "@type": "DeleteResourceOperation",
        "method": "DELETE"
      }
    ]
  }

CRUD Operations on a Plone collection::

  {
    "@context": "http://www.w3.org/ns/hydra/context.jsonld",
    "@id": "http://localhost:8080/Plone/"
    "@type": "Collection",
    "operation": [
        {
            "@type": "CreateResourceOperation",
            "name": "Create Resource",
            "method": "POST",
            "expects": {
                "supportedProperty": [
                    {
                        "@type": "PropertyValueSpecification",
                        "hydra:property": "id",
                        "hydra:required": "true",
                        "readOnlyValue": "true"
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
            "method": "PUT",
        },
        {
            "@type": "DeleteResourceOperation",
            "name": "Delete Resource",
            "method": "DELETE",
        }
    ]
  }
