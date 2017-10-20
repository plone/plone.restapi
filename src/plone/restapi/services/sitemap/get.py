# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Sitemap(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            'sitemap': {
                '@id': '{}/@sitemap'.format(self.context.absolute_url()),
            },
        }
        if not expand:
            return result

        sitemap = getMultiAdapter((self.context, self.request),name="sitemap.xml.gz")
        items = []
        for entry in sitemap.objects():
            items.append(entry)
        result['sitemap']['items'] = items
        return result


class SitemapGet(Service):

    def reply(self):
        sitemap = Sitemap(self.context, self.request)
        return sitemap(expand=True)['sitemap']
