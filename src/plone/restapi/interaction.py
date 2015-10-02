# -*- coding: utf-8 -*-
from Acquisition import aq_inner
from Acquisition import aq_parent
from Products.CMFCore.utils import getToolByName

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
from zope.component import getMultiAdapter, queryMultiAdapter


@implementer(ISerializeToJson)
@adapter(IDexterityContent)
class SerializeToJson(object):

    def __init__(self, context):
        context = aq_inner(context)
        self.context = context
        self.atool = getToolByName(context, "portal_actions")
        self.ttool = getToolByName(context, "portal_types")

    def getActions(self, category=None):
        actions = []
        actions.extend([dict(x) for x in self.ttool.listActionInfos(
            object=self.context,
            category=category,
            max=-1,
        )])
        actions.extend([dict(x) for x in self.atool.listActionInfos(
            object=self.context,
            categories=(category, ),
            max=-1,
        )])

        return actions

    def __call__(self):

        result = queryAdapter(
            self.context,
            interface=ISerializeToJson,
            name='content',
            default={})

        result['actions'] = {
            'user': self.getActions('user'),
            'object': self.getActions('object'),
            'portal_tabs': self.getActions('portal_tabs'),
            'object_buttons': self.getActions('object_buttons'),
            'document': self.getActions('document_actions'), # Workflow, edit, view, sharing, display, default
            'site': self.getActions('site_actions')
        }

        return result
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
        return result

