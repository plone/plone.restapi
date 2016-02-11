# -*- coding: utf-8 -*-
from plone.app.contenttypes.interfaces import ICollection
from plone.restapi.interfaces import ISerializeToJson
from plone.restapi.serializer.dxcontent import SerializeToJson
from zope.component import adapter
from zope.interface import Interface
from zope.interface import implementer
from zope.site.hooks import getSite


@implementer(ISerializeToJson)
@adapter(ICollection, Interface)
class SerializeCollectionToJson(SerializeToJson):

    def __call__(self):
        result = super(SerializeCollectionToJson, self).__call__()
        portal = getSite()
        result['member'] = [
            {
                '@id': '{0}/{1}'.format(
                    portal.absolute_url(),
                    '/'.join(member.getPhysicalPath())
                ),
                'title': member.title,
                'description': member.description
            }
            for member in self.context.results()
        ]
        return result
