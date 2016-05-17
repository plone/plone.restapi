# -*- coding: utf-8 -*-
from plone.rest import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

MOCKEDRESPONSE = {
    "actions": [{
        "@id": "view",
        "title": "View",
        "category": ""
    }, {
        "@id": "edit",
        "title": "Edit",
        "category": ""
    }, {
        "@id": "Collection",
        "title": "Collection",
        "category": "factories"
    }, {
        "@id": "Document",
        "title": "Document",
        "category": "factories"
    }, {
        "@id": "reject",
        "title": "Send back",
        "category": "workflow"
    }]
}


class ActionsGet(Service):

    implements(IPublishTraverse)

    def render(self):
        return MOCKEDRESPONSE
