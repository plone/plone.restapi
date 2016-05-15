# -*- coding: utf-8 -*-
from plone.rest import Service
from zope.interface import implements
from zope.publisher.interfaces import IPublishTraverse

MOCKEDRESPONSE = {
    'object_actions': [
        {
            '@id': 'Collection',
            'title': 'Collection',
            'uri': 'http://localhost:8080/Plone/++add++Collection',
            'category': 'factories',
        },
        {
            '@id': 'Document',
            'title': 'Document',
            'uri': 'http://localhost:8080/Plone/++add++Document',
            'category': 'factories',
        },
        {
            '@id': 'reject',
            'title': 'Send back',
            'uri': 'http://localhost:8080/Plone//content_status_modify?workflow_action=reject',
            'category': 'workflow',
        },
    ]
}


class ActionsGet(Service):

    implements(IPublishTraverse)

    def render(self):
        return MOCKEDRESPONSE
