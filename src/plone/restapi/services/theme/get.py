# -*- coding: utf-8 -*-
from plone.rest import Service

MOCKEDRESPONSE = {
    "href": "http://plone/++theme++mytheme/style/main.css"
}


class ThemeEditedResource(Service):

    def render(self):
        resource = self.request.form.get('resource')
        if resource == '/style/main.css':
            return MOCKEDRESPONSE
        else:
            self.request.response.setStatus(404)
