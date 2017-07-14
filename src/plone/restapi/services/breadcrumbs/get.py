# -*- coding: utf-8 -*-
from plone.restapi.services import Service
from zope.component import getMultiAdapter


class BreadcrumbsGet(Service):

    def reply(self):
        breadcrumbs_view = getMultiAdapter((self.context, self.request),
                                           name="breadcrumbs_view")
        result = {
            '@id': '{}/@breadcrumbs'.format(
                self.context.absolute_url()
            ),
            'items': []
        }
        for crumb in breadcrumbs_view.breadcrumbs():
            result['items'].append({
                'title': crumb['Title'],
                'url': crumb['absolute_url']
            })
        return result
