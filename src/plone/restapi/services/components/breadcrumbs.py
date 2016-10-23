# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import Interface
from zope.interface import implementer


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Breadcrumbs(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        if not expand:
            return {'@components': {'breadcrumbs': {
                '@id': '{}/@components/breadcrumbs'.format(
                    self.context.absolute_url()),
            }}}

        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name="breadcrumbs_view")
        result = []
        for crumb in breadcrumbs_view.breadcrumbs():
            result.append({
                'title': crumb['Title'],
                'url': crumb['absolute_url']
            })
        return {'@components': {'breadcrumbs': result}}
