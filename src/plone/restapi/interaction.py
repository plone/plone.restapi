# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.interfaces import IPropertiesTool
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.textfield import RichText
from plone.app.contenttypes.interfaces import ICollection
from plone.app.contenttypes.interfaces import IFile
from plone.app.contenttypes.interfaces import IImage
from plone.dexterity.interfaces import IDexterityContent
from plone.namedfile.file import NamedBlobImage
from plone.restapi.utils import get_object_schema
from plone.restapi.interfaces import IContext
from plone.restapi.interfaces import ISerializeToJson

from zope.site.hooks import getSite
from zope.schema import Datetime
from zope.interface import implementer
from zope.component import adapter
from zope.component import getUtility
from zope.component import queryAdapter



@implementer(ISerializeToJson)
@adapter(IDexterityContent)
def SerializeToJson(context):
    result = queryAdapter(
        context,
        interface=ISerializeToJson,
        name='content',
        default={})
    result['actions'] = {
        'user': {},
        'document': {},
        'site': {},
        'parents': {}
    }
    # Operations
    # result["operation"] = [
    #     {
    #         "@type": "CreateResourceOperation",
    #         "name": "Create Resource",
    #         "method": "POST",
    #         "expects": {
    #             "supportedProperty": [
    #                 {
    #                     "@type": "PropertyValueSpecification",
    #                     "hydra:property": "id",
    #                     "hydra:required": "true",
    #                     "readOnlyValue": "true"
    #                 },
    #                 {
    #                     "@type": "PropertyValueSpecification",
    #                     "hydra:property": "title",
    #                     "hydra:required": "true",
    #                     "readOnlyValue": "false"
    #                 },
    #             ],
    #         }
    #     },
    #     {
    #         "@type": "ReplaceResourceOperation",
    #         "name": "Update Resource",
    #         "method": "PUT",
    #     },
    #     {
    #         "@type": "DeleteResourceOperation",
    #         "name": "Delete Resource",
    #         "method": "DELETE",
    #     }
    # ]
    return {}
