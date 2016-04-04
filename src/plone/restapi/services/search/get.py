# -*- coding: utf-8 -*-
from plone.rest import Service
from plone.restapi.search.handler import SearchHandler


class SearchGet(Service):

    def render(self):
        query = self.request.form.copy()
        return SearchHandler(self.context, self.request).search(query)
