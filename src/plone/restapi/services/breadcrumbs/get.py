# -*- coding: utf-8 -*-
from plone.restapi.interfaces import IExpandableElement
from plone.restapi.services import Service
from zope.component import adapter
from zope.component import getMultiAdapter
from zope.interface import implementer
from zope.interface import Interface


@implementer(IExpandableElement)
@adapter(Interface, Interface)
class Breadcrumbs(object):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self, expand=False):
        result = {
            "breadcrumbs": {
                "@id": "{}/@breadcrumbs".format(self.context.absolute_url())
            }
        }
        if not expand:
            return result

        breadcrumbs_view = getMultiAdapter(
            (self.context, self.request), name="breadcrumbs_view"
        )
        items = []
        for crumb in breadcrumbs_view.breadcrumbs():

            items.append(
                {
                    "title": crumb["Title"],
                    "@id": crumb["absolute_url"],
                    "nav_title": crumb.get("nav_title", None),
                }
            )

        result["breadcrumbs"]["items"] = items
        return result


class BreadcrumbsGet(Service):
    def reply(self):
        breadcrumbs = Breadcrumbs(self.context, self.request)
        return breadcrumbs(expand=True)["breadcrumbs"]
