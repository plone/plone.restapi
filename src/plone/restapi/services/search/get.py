# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.search.handler import SearchHandler
from plone.restapi.search.utils import unflatten_dotted_dict


class SearchGet(Service):

    def render(self):
        query = self.request.form.copy()
        query = unflatten_dotted_dict(query)
        return SearchHandler(self.context, self.request).search(query)
